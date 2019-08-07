#!/usr/bin/env bash

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/data_word_based_delex/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/model_word_based_delex/1/"

mkdir -p $EXPT_PATH

# data preprocessing

#python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt -src_seq_length 39 -valid_src $DATA_PATH/dev_src.txt -valid_tgt $DATA_PATH/dev_tgt.txt -tgt_seq_length 33 -save_data $DATA_PATH


# 1: adam initial learning rate 0.001, use bidirectional rnn instead of unidirectional rnn in encoder
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
# -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -encoder_type brnn\
# -batch_size 20 -word_vec_size 50 -rnn_size 128 -epochs 20 -start_checkpoint_at 5 -dropout 0.0 -global_attention mlp >& $EXPT_PATH/train.log &

wait

# test on test data
#python ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/_acc_*_e13.pt -src $DATA_PATH/test_src.txt -output $EXPT_PATH/test_e13.txt -verbose -gpu 0 -max_length 35 -beam_size 10 >& $EXPT_PATH/test_e13.log &

wait

# post process and evaluate
bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  $EXPT_PATH/test_e13.txt word-delex $DATA_PATH/../data_word_based/test_multi_ref_references.txt $DATA_PATH/test_relex.txt