from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification, Trainer
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import json
import torch
import torch.nn.functional as F
from tqdm import tqdm
import wandb
import os
import numpy as np
from module.evaluation import metrics_report, metrics_report_for_emo_binary, FocalLoss
from module.dataset import get_bulk_texts_and_labels
import datetime
import logging

emotion_label_policy = {'angry': 0, 'anger': 0,
    'disgust': 1,
    'fear': 2,
    'happy': 3, 'happines': 3, 'happiness': 3, 'excited': 3,
    'sad': 4, 'sadness': 4, 'frustrated': 4,
    'surprise': 5, 'surprised': 5, 
    'neutral': 6}    

class Finetuner:
    def __init__(self, gpus, model_name, train_data, test_data, data_label, model_label, use_wandb, batch_size, epoch, learning_rate, **kwargs):
        # Finetuner가 받아오는 인자들
        self.model_name = model_name
        self.train_data = train_data
        self.test_data = test_data
        
        self.use_wandb = use_wandb
        self.gpus = gpus
        self.batch_size = batch_size
        self.epoch = epoch
        self.learning_rate = learning_rate
        self.model_type = 1
            # 1: AutoModel에다가 바로 Linear layer (hidden_size ➝ n_emotion)
            # 2: AutoModelForSequenceClassification에다가 Linear layer (original_topology ➝ n_emotion)
            # 3: Automodel에다가 Transformer layer n개 붙인 뒤 Linear layer (hidden_size ➝ n_emotion)
            
        # logging 용
        self.start_time = datetime.datetime.now()
        self.data_label = data_label
        self.model_label = model_label
        self.class_label = np.array(['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'])
        self.log_directory = kwargs.get('log_directory', None)
        
        self.logger_train = self.set_logger('train')
        self.logger_test = self.set_logger('test')

        # 모델이 자체적으로 생성
        '''
        a_model = 원래 모델 (사전학습된 감정분류 모델)
        b_model = a_model 위에 추가된 모델 (a_model에 Linear layer를 추가한 모델)
        '''
        
        if self.model_type == 1:
            self.a_model = self.set_a_model(self.model_name)
            self.original_topology = len(self.a_model.config.label2id) # original model's output size
            self.b_model = self.set_b_model_as_added_layer(model_name, self.original_topology, num_classes=7)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    def set_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)    
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_name = f'{logger_name}_{self.model_label}_{self.data_label}-{str(self.start_time)}.log'
        if self.log_directory:
            if not os.path.exists(f'{self.log_directory}'):
                os.makedirs(f'{self.log_directory}')
            if not os.path.exists(f'{self.log_directory}/{logger_name}_{self.model_label}'):
                os.makedirs(f'{self.log_directory}/{logger_name}_{self.model_label}')
            file_handler = logging.FileHandler(f'{self.log_directory}/{logger_name}_{self.model_label}/{file_name}')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_dataset_from_file(self, filename):
        # Load the JSON dataset
        device = 'cuda:0'
        
        with open(filename) as f:
            data = json.load(f)
        texts = []
        labels_text = []
        for doc in data.values():
            for utt in doc[0]:
                texts.append(utt['utterance'])
                labels_text.append(utt['emotion'])
        encoded_texts = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        
        # Process labels to number tensor
        labels_number = [emotion_label_policy[i] for i in labels_text]      # 'text labels from data' to 'number labels'

        input_ids = encoded_texts['input_ids'].to(device)
        attention_masks = encoded_texts['attention_mask'].to(device)
        labels = torch.tensor(labels_number).to(device)
        
        dataset = TensorDataset(input_ids, attention_masks, labels)
        return dataset
    
    def set_b_model_as_added_layer(self, model_name, original_topology=7, num_classes=7):
        '''
        Pre-trained Classificaiton 모델 (LM + classification layer) 위에다 또 linear layer를 얹어서
        추가된 linear layer에 분류를 학습
        이 함수는 추가 linear layer(added_model)를 리턴한다
        '''
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Freeze the pre-trained model's parameters
        for param in model.parameters():
            param.requires_grad = False
            
        model.classifier = nn.Sequential(
            nn.Linear(in_features=original_topology, out_features=num_classes),
            # nn.ReLU(),
            # nn.Dropout(p=0.1),
            # nn.Linear(in_features=num_classes, out_features=num_classes)
        )
        added_model = model.classifier
        return added_model
    
    def finetune(self):
        # Initialize WandB
        if self.use_wandb:
            wandb_project_name = f'{self.model_label}_train_on_{self.data_label}'
            wandb.init(project=wandb_project_name)
        
        self.a_model = self.a_model.cuda()
        self.b_model = self.b_model.cuda()
        
        optimizer = optim.Adam(self.b_model.parameters(), lr=self.learning_rate)
        dataset = self.get_dataset_from_file(self.train_data)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        
        i = 0
        for epoch in range(self.epoch):
            loss_overall = 0.0 # logging에 쓸 loss 값 저장용
            loss_wandb = 0.0
            '''
            학습하면서 train 데이터에 대해 logging도 수행
            '''
            emotion_pred, emotion_label = [list() for _ in range(2)]
        
            for inputs, masks, labels in tqdm(dataloader, desc=f"Train | Epoch {epoch+1}"):
                
                optimizer.zero_grad()
                model_outputs = self.a_model(inputs, masks)[0]
                outputs = self.b_model(model_outputs)
                
                criterion = FocalLoss(gamma=2)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                
                for pred in outputs:
                    emotion_pred.append(pred)
                for label in labels:
                    emotion_label.append(label)
                
                loss_overall += loss.item() * inputs.size(0)
                if self.use_wandb:
                    loss_wandb += loss.item() * inputs.size(0)
                    if i % 100 == 99:  # Log every 100 mini-batches
                        wandb.log({'train_loss': loss_wandb / 100})
                        loss_wandb = 0.0
                    i+=1
                    
            emotion_pred = torch.stack(emotion_pred).cpu()
            emotion_label = torch.stack(emotion_label).cpu()
            
            epoch_loss = loss_overall / len(dataset)
            self.logger_train.info('\nEpoch [{}/{}], Loss: {:.4f}'.format(epoch+1, self.epoch, epoch_loss))
            
            self.reporting(emotion_pred, emotion_label, type_label='train')
            # 현재 epoch에 대해서 모델 테스트
            self.test(epoch)
            
        # Finish the WandB run
        if self.use_wandb:
            wandb.finish()
            
        self.save_model()
    
    def test(self, epoch_num):
        device = 'cuda:0'
        dataset = self.get_dataset_from_file(self.test_data)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        
        with torch.no_grad():
            emotion_pred, emotion_label = [list() for _ in range(2)]
            loss_overall = 0.0 # logging에 쓸 loss 값 저장용
            for inputs, masks, labels in tqdm(dataloader, desc=f"Test | Epoch {epoch_num+1}"):
                model_outputs = self.a_model(inputs, masks)[0]
                outputs = self.b_model(model_outputs)
                
                criterion = FocalLoss(gamma=2)
                loss = criterion(outputs, labels)
                loss_overall += loss.item() * inputs.size(0)
                
                for pred in outputs:
                    emotion_pred.append(pred)
                for label in labels:
                    emotion_label.append(label)
        
        emotion_pred = torch.stack(emotion_pred).cpu()          # 펴서 tensor로 만들어줌
        emotion_label = torch.stack(emotion_label).cpu()        # 펴서 tensor로 만들어줌
        self.logger_test.info('\nEpoch [{}/{}]'.format(epoch_num+1, self.epoch))
        self.reporting(emotion_pred, emotion_label, type_label='test')
        
    def run(self, **kwargs):
        self.finetune()
    
    def reporting(self, emotion_pred, emotion_true, type_label='test'):
        '''
        input: emotion_pred, emotion_true, class_label
        - emotion_pred: torch.tensor (utterance 개수, num_classes)
        - emotion_true: torch.tensor (utterance 개수)
        - class_label: np.array (각 index가 가리키는 감정의 label(text)) 
        '''
        class_label = self.class_label
        model_label = self.model_label
        log_label = self.data_label
        start_time = self.start_time
        
        report = '\n'
        report += metrics_report(emotion_pred, emotion_true, class_label)
        report += '\n'+metrics_report_for_emo_binary(emotion_pred, emotion_true)+'\n'
        
        if type_label == 'train':
            self.logger_train.info(report)
        else:
            self.logger_test.info(report)    # report를 log에 저장
        
        # report를 파일에 저장
        with open(f'log/{model_label}-{type_label}_{log_label}-{str(start_time)}.txt', 'a') as f:
            f.write(report)
    
    def set_a_model(self, model_name):
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        # Freeze the pre-trained model's parameters
        for param in model.parameters():
            param.requires_grad = False
        return model
    
    def save_model(self):
        torch.save(self.b_model.state_dict(), f'model/{self.model_label}_{self.data_label}.pt')
    
    def set_model_with_replaced_layer(self, model_name, num_classes=7):
        ''' 
        개선필요
        Pre-trained Classification 모델에서 LM만 가져와서 분류 역할은 새로운 linear layer만 맡게 된다
        그러므로 set_b_model_as_added_layer에 비해 분류 layer가 하나 적다
        '''
        model = AutoModel.from_pretrained(model_name)
        
        # Freeze the pre-trained model's parameters
        for param in model.parameters():
            param.requires_grad = False
            
        model.classifier = nn.Sequential(
            nn.Linear(in_features=self.original_topology, out_features=num_classes),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(in_features=num_classes, out_features=num_classes)
        )
        added_model = model.classifier
        return added_model





