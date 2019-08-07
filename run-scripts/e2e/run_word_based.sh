#!/usr/bin/env bash

OPENNMT_PATH="../../openNMT-py"
NLG_EVAL_CODE_PATH="../../data"
DATA_PATH="../../datasets/e2e/preprocessed/word_based/"
EXPT_PATH="../../experiments/e2e/word_based/"
MODEL_NAME="word_based"

mkdir -p $EXPT_PATH

# number of models to be trained/evaluated in parallel
N=${1:-1}
TEST_FILE_BASE=${2:-dev_multi_ref}"_"

# preprocess data for OpenNMT-py
PREPROCESS=true # true, false
if [ "$PREPROCESS" = true ]
then
	python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt\
	-src_seq_length 500 -valid_src $DATA_PATH/dev_src.txt -valid_tgt $DATA_PATH/dev_tgt.txt -tgt_seq_length 500\
	-save_data $DATA_PATH &
fi

# train
EPOCHS=13
MODEL_HYPERPARAMS=" -enc_layers 1 -dec_layers 1 -encoder_type rnn -word_vec_size 64 -rnn_size 64 -batch_size 64 "
OPTIMIZER_HYPERPARAMS="-optim sgd -learning_rate 1.0 -learning_rate_decay 0.5 -epochs $EPOCHS"

num_models=($(seq 1 1 $N))

TRAIN=true # true, false
if [ "$TRAIN" = true ]
then
	printf "Training models "
	printf "%s, " "${num_models[@]}"
	for NUM_MODEL in "${num_models[@]}"
	do
		nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH/"$MODEL_NAME"_"$NUM_MODEL" -gpuid 0\
		$MODEL_HYPERPARAMS $OPTIMIZER_HYPERPARAMS -seed "$NUM_MODEL" -overwrite_checkpoints  >& $EXPT_PATH/train_"$MODEL_NAME"_"$NUM_MODEL".log &
	done
	wait
fi

# generation
BEAM_SIZE=15
TEST_FILE_SRC=$DATA_PATH/"$TEST_FILE_BASE"src.txt
TEST_FILE_TGT_OUTPUTS=$EXPT_PATH/"$TEST_FILE_BASE"tgt.txt

GENERATE=true # true, false
if [ "$GENERATE" = true ]
then
	printf "Generating texts for %s\n" "$TEST_FILE_BASE"
	TEST_FILE_SRC=$DATA_PATH/"$TEST_FILE_BASE"src.txt
	for NUM_MODEL in "${num_models[@]}"
	do
		TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$MODEL_NAME"_"$NUM_MODEL"_hypotheses.txt

		nohup python -u ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/"$MODEL_NAME"_"$NUM_MODEL".pt -src $TEST_FILE_SRC\
		-output "$TEST_FILE_TGT_HYPOTHESES" -gpu 0 -max_length 77 -n_best 1 -beam_size $BEAM_SIZE \
		>& $EXPT_PATH/generate_"$TEST_FILE_BASE""$MODEL_NAME"_"$NUM_MODEL".log &
	done
    wait
fi

# evaluation
EVALUATE=true #true, false
if [ "$EVALUATE" = true ]
then
	printf "Evaluating texts for %s\n" "$TEST_FILE_BASE"
	for NUM_MODEL in "${num_models[@]}"
	do
		TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$MODEL_NAME"_"$NUM_MODEL"_hypotheses.txt

		bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  "$TEST_FILE_TGT_HYPOTHESES" word-delex\
		$DATA_PATH/"$TEST_FILE_BASE"lexicalized_tgt.txt $DATA_PATH/"$TEST_FILE_BASE"relex.txt &
	done
	wait
fi
