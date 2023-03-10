import argparse
import json
import os
import random
import csv
from typing import List

from module.tester import Tester

import numpy as np
import torch

# Reproducibility setting
def set_random_seed(seed: int):
    random_seed = seed
    torch.manual_seed(random_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(random_seed)
    random.seed(random_seed)
    torch.cuda.manual_seed(random_seed)
    torch.cuda.manual_seed_all(random_seed)
    
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Training Environment
    parser.add_argument('--gpus', default=[1])
    parser.add_argument('--num_process', default=int(os.cpu_count() * 0.8), type=int)
    parser.add_argument('--num_worker', default=6, type=int)
    parser.add_argument('--port', default=1234, type=int)

    parser.add_argument('--model_name', default="j-hartmann/emotion-english-distilroberta-base")
    parser.add_argument('--different_topology', default=False)  # pretrained emotion classification model to test has different emotion topology as DailyDialog
    parser.add_argument('--topology', default=None)             # The number of emotion classes in the model (if the model has different topology)
    parser.add_argument('--epoch', default=10, type=int)        # When fine-tuning is required
    parser.add_argument('--dropout', default=0.5, type=float)   # When fine-tuning is required
    
    parser.add_argument('--test_data', default="data/data_fold/data_0/dailydialog_test.json")
    parser.add_argument('--log_directory', default='logs', type=str)
    parser.add_argument('--data_label', help='the label that attaches to saved model', default='dailydialog_fold_0')

    parser.add_argument('--max_seq_len', help='the max length of each tokenized utterance', default=75, type=int)
    return parser.parse_args()

def test_preconditions(args: argparse.Namespace):
    assert args.model_name is not None, "For test, load emotion classification model."

def main():
    args = parse_args()

    test_preconditions(args)
    set_random_seed(77)
    
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join([str(_) for _ in args.gpus])
    
    model_name = ["j-hartmann/emotion-english-distilroberta-base", "j-hartmann/emotion-english-roberta-large"]
    model_label = ['j-hartmann distill roberta base', 'j-hartmann roberta large']
    # model_name = ["j-hartmann/emotion-english-roberta-large"]
    # model_label = ['j-hartmann roberta large']
    # model_name = ["j-hartmann/emotion-english-distilroberta-base"]
    # model_label = ['j-hartmann distill roberta base']
    
    
    test_datas = ['data_fold/data_0/dailydialog_test.json', * 
                 [f'data_fold/data_{fold_}/data_{fold_}_test.json' for fold_ in range(1, 5)]]
    data_labels = ['-original_dd', *[f'-data_{fold_}_DailyDialog' for fold_ in range(1, 5)]]
    
    for mn, ml in zip(model_name, model_label):
        tester = Tester(mn, ml, test_datas, data_labels)
        tester.run()

        del tester

if __name__ == '__main__':
    main()