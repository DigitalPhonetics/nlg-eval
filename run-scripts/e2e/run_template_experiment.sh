#!/usr/bin/env bash

#DATA_PATH="/home/users0/jagfelga/slu-work/NLG/E2E/data_template/"
#EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/E2E/model_template_word_delex/"

OPENNMT_PATH="../../openNMT-py"
NLG_EVAL_CODE_PATH="../../data"
DATA_PATH="../../datasets/e2e/preprocessed/template/"
EXPT_PATH="../../experiments/e2e/template/"
MODEL_NAME="word_based"

# number of models to be trained/evaluated in parallel
N=${1:-1}
TEMPLATE="$2" # 1, 2, 1+2

DATA_PATH_TEMPLATE="$DATA_PATH"/template_"$TEMPLATE"/
EXPT_PATH_TEMPLATE="$EXPT_PATH"/template_"$TEMPLATE"/

mkdir -p $EXPT_PATH_TEMPLATE

# data preprocessing
PREPROCESS=true # true , false
if [ "$PREPROCESS" = true ]
    then
	python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH_TEMPLATE/train_src.txt -train_tgt $DATA_PATH_TEMPLATE/train_tgt.txt\
	 -src_seq_length 4000 -valid_src $DATA_PATH_TEMPLATE/dev_src.txt -valid_tgt $DATA_PATH_TEMPLATE/dev_tgt.txt\
	  -tgt_seq_length 4000 -save_data $DATA_PATH_TEMPLATE/ &
    wait
fi

# train

HYPERPARAMS_T1=" -enc_layers 1 -dec_layers 1 -rnn_size 64 -encoder_type rnn -word_vec_size 28 -batch_size 4 -optim adam -learning_rate 0.001 -dropout 0.4 -epochs 25"
HYPERPARAMS_T2=" -enc_layers 1 -dec_layers 1 -rnn_size 64 -encoder_type rnn -word_vec_size 28 -batch_size 4 -optim sgd -learning_rate 1.0  -dropout 0.5 -epochs 13"
HYPERPARAMS_T12=" -enc_layers 1 -dec_layers 1 -rnn_size 64 -encoder_type brnn -word_vec_size 30 -batch_size 16 -optim sgd -learning_rate 1.0  -dropout 0.3 -epochs 15"

HYPERPARAMS=$HYPERPARAMS_T1
if [ "$TEMPLATE" = 2 ]
    then
	HYPERPARAMS=$HYPERPARAMS_T2
elif [ "$TEMPLATE" = 1+2 ]
	then
	HYPERPARAMS=$HYPERPARAMS_T12
fi

num_models=($(seq 1 1 $N))

TRAIN=true # true , false
if [ "$TRAIN" = true ]
    then
    for NUM_MODEL in "${num_models[@]}"
    do
		nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH_TEMPLATE -save_model "$EXPT_PATH_TEMPLATE"/template_"$TEMPLATE"_model_"$NUM_MODEL"\
		  -gpuid 0 $HYPERPARAMS -overwrite_checkpoints -seed $NUM_MODEL >& "$EXPT_PATH_TEMPLATE"/train_template_"$TEMPLATE"_model_"$NUM_MODEL".log &
    done
    wait
fi

TEST_FILE="../../datasets/e2e/test_template_10_random_inputs.txt"
BEAM=30

# generate
GENERATE=true # true , false
if [ "$GENERATE" = true ]
    then
    for NUM_MODEL in "${num_models[@]}"
    do
		TEST_FILE_TGT_HYPOTHESES="$EXPT_PATH_TEMPLATE"/test_"$NUM_MODEL".txt
		python ${OPENNMT_PATH}/translate.py -model "$EXPT_PATH_TEMPLATE"/template_"$TEMPLATE"_model_"$NUM_MODEL".pt\
		 -src $TEST_FILE -output $TEST_FILE_TGT_HYPOTHESES -gpu 0 -max_length 77\
		 -n_best $BEAM -verbose -beam_size $BEAM >& "$EXPT_PATH_TEMPLATE"/generate_test_"$NUM_MODEL".log &
    done
	wait
fi