from transformers import AutoTokenizer, AutoModelForMaskedLM, Trainer, AutoModelForSequenceClassification
import json

class SimpleDataset:
    def __init__(self, tokenized_texts):
        self.tokenized_texts = tokenized_texts
    
    def __len__(self):
        return len(self.tokenized_texts["input_ids"])
    
    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.tokenized_texts.items()}

def get_dataset(model_name, datafile):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    with open(datafile, 'r') as f:
        data = json.load(f)
    
    utterances = []
    for doc in data.values():
        for utt in doc[0]:
            utterances.append(utt['utterance'])
            
    tokenized_texts = tokenizer(utterances,truncation=True,padding=True)
    dataset = SimpleDataset(tokenized_texts)
    return dataset

def get_labels(test_file):
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    emotion_labels = []
    for doc in data.values():
        for utt in doc[0]:
            emotion_labels.append(utt['emotion'])
    
    return emotion_labels

def get_bulk_texts_and_labels(test_file):
    '''
    파일에서 각 utterance의 text와 emotion label 순서대로 두 list를 반환한다 (text 형태로)
    ex): ['neutral', 'angry', 'neutral', ...]
    '''
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    texts = []
    labels_text = []
    for doc in data.values():
        for utt in doc[0]:
            texts.append(utt['utterance'])
            labels_text.append(utt['emotion'])
    
    return (texts, labels_text)