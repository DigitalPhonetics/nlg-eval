#!/usr/bin/env bash

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Laptop/data_character_based/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Laptop/model_character_based/1/"

mkdir -p $EXPT_PATH

# data preprocessing
#python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt\
# -src_seq_length 340 -valid_src $DATA_PATH/dev_src.txt\
#  -valid_tgt $DATA_PATH/dev_tgt.txt -tgt_seq_length 419\
#   -save_data $DATA_PATH -character_based

# vocab size 48 for src + 49 tgt

# 1: Goyal set-up (do not know word vec size though)
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
# -word_vec_size 100 -rnn_size 300 -batch_size 20 -global_attention mlp\
# -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -start_checkpoint_at 5\
# >& $EXPT_PATH/train.log &

wait

# test on test data
EPOCH=13
python ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/_acc_*_e$EPOCH.pt -src $DATA_PATH/test_multi_ref.txt -output $EXPT_PATH/test_e$EPOCH.txt -verbose -gpu 0 -character_based -max_length 420 >& $EXPT_PATH/test_e$EPOCH.log &

wait

# post process and evaluate
bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  $EXPT_PATH/test_e$EPOCH.txt character $DATA_PATH/test_multi_ref_references.txt