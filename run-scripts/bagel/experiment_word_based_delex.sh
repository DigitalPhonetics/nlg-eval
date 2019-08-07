#!/usr/bin/env bash

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/BAGEL/cv_word_based_delex/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/BAGEL/cv_model_word_based_delex/1/"

# data preprocessing
for FOLD in $DATA_PATH/*/; do
    FOLD_NO=$(basename "$FOLD")

    EXPT_PATH_FOLD=$EXPT_PATH/$FOLD_NO/

    #mkdir -p $EXPT_PATH_FOLD
    #echo $EXPT_PATH_FOLD

    #python $OPENNMT_PATH/preprocess.py -train_src $FOLD/train_src.txt -train_tgt $FOLD/train_tgt.txt\
    # -src_seq_length 35 -valid_src $FOLD/dev_src.txt -valid_tgt $FOLD/dev_tgt.txt\
    #  -tgt_seq_length 27 -save_data $EXPT_PATH_FOLD
done
wait

for FOLD in $DATA_PATH/*; do
    FOLD_NO=$(basename "$FOLD")

    EXPT_PATH_FOLD=$EXPT_PATH/$FOLD_NO/

    # 1: adam initial learning rate 0.001, use bidirectional rnn instead of unidirectional rnn in encoder
    #nohup python -u $OPENNMT_PATH/train.py -data $EXPT_PATH_FOLD -save_model $EXPT_PATH_FOLD -gpuid 0\
    # -optim adam -learning_rate 0.001 -enc_layers 1 -dec_layers 1 -encoder_type brnn\
    # -batch_size 20 -word_vec_size 50 -rnn_size 128 -epochs 100 -start_checkpoint_at 90\
    # -dropout 0.0 -global_attention mlp >& $EXPT_PATH_FOLD/train.log &
done
wait

for FOLD in $DATA_PATH/*; do
    FOLD_NO=$(basename "$FOLD")
    EXPT_PATH_FOLD=$EXPT_PATH/$FOLD_NO/

    echo $EXPT_PATH_FOLD

    # test on test data
    python ${OPENNMT_PATH}/translate.py -model $EXPT_PATH_FOLD/_acc_*_e100.pt\
     -src $FOLD/test_src.txt -output $EXPT_PATH_FOLD/test_e13.txt -verbose\
     -gpu 0 -max_length 27 -beam_size 20 >& $EXPT_PATH_FOLD/test_e100.log &
     exit
done

wait

for FOLD in $DATA_PATH/*; do
    FOLD_NO=$(basename "$FOLD")

    EXPT_PATH_FOLD=$EXPT_PATH/$FOLD_NO/
    # post process and evaluate
    #bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  $EXPT_PATH_FOLD/test_e1000.txt word-delex\
    # $FOLD/test_tgt.txt $DATA_PATH/test_relex.txt
done