#!/usr/bin/env bash

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
CORPUS_PATH="/home/users0/jagfelga/slu-work/RNNLG-Restaurant/data/original_data/complete_dataset_released_after_challenge"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/data_word_based_delex/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/model_baseline_template_delex/1/"

mkdir -p $EXPT_PATH

# 1: first target
# 2: longest target
# 3: random target

# data preprocessing - use data of data_word_based_delex as input, data_word_based for test references

# run baseline on test data
python $NLG_EVAL_CODE_PATH/../baseline.py $DATA_PATH/train.txt preprocessed $DATA_PATH/test_src.txt --output_path $EXPT_PATH/data_generated_test.txt > $EXPT_PATH/baseline.log &

wait

# post process and evaluate
bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  $EXPT_PATH/data_generated_test.txt word-delex $DATA_PATH/../data_word_based/test_multi_ref_references.txt $DATA_PATH/test_relex.txt