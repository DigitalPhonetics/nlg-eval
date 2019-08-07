#!/usr/bin/env bash

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/data_character_based/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/model_character_based/4/"

mkdir -p $EXPT_PATH

# data preprocessing
#python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt\
# -src_seq_length 210 -valid_src $DATA_PATH/dev_src.txt\
#  -valid_tgt $DATA_PATH/dev_tgt.txt -tgt_seq_length 175\
#   -save_data $DATA_PATH -character_based

# vocab size 47 for src + tgt

# 1: adam initial learning rate 0.001, use bidirectional rnn instead of unidirectional rnn in encoder
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
# -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -encoder_type brnn\
# -batch_size 20 -word_vec_size 50 -rnn_size 128 -epochs 20 -start_checkpoint_at 5 -dropout 0.3 >& $EXPT_PATH/train.log &

# 2: e2e character-based set-up
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
# -optim adam -learning_rate 0.001 -enc_layers 2 -dec_layers 2 -max_grad_norm 2.0 -start_checkpoint_at 5 >& $EXPT_PATH/train.log &

# 3: Goyal set-up (do not know word vec size though)
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
# -word_vec_size 100 -rnn_size 300 -batch_size 20 -global_attention mlp\
# -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -start_checkpoint_at 5\
# >& $EXPT_PATH/train.log &

# 4: modified Goyal set up, no lr decay, no dropout
nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0\
 -word_vec_size 50 -rnn_size 300 -batch_size 20 -global_attention mlp\
 -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -start_checkpoint_at 5 -dropout 0.0\
 -start_decay_at 21 -epochs 20 -l2_regularization_weight 0.00001\
 >& $EXPT_PATH/train.log &

wait

# test on test data
EPOCH=20
python ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/_acc_*_e$EPOCH.pt -src $DATA_PATH/test_multi_ref.txt -output $EXPT_PATH/test_e$EPOCH.txt -verbose -gpu 0 -character_based -max_length 175 >& $EXPT_PATH/test_e$EPOCH.log &

wait

# post process and evaluate
bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  $EXPT_PATH/test_e$EPOCH.txt character $DATA_PATH/test_multi_ref_references.txt