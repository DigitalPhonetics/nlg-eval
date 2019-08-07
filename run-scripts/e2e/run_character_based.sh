#!/usr/bin/env bash

OPENNMT_PATH="../../openNMT-py"
NLG_EVAL_CODE_PATH="../../data"
DATA_PATH="../../datasets/e2e/preprocessed/character_based/"
EXPT_PATH="../../experiments/e2e/character_based/"
MODEL_NAME="character_based"

mkdir -p $EXPT_PATH

# number of models to train/generate for/evaluate in parallel
N=$1
# enter test to generate for/evaluate on test split, else uses dev split
TEST_FILE_BASE=${2:-dev_multi_ref}"_"

# preprocess data for OpenNMT-py
PREPROCESS=true # true, false
if [ "$PREPROCESS" = true ]
    then
    python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt\
     -src_seq_length 500 -valid_src $DATA_PATH/dev_src.txt -valid_tgt $DATA_PATH/dev_tgt.txt -tgt_seq_length 500\
     -save_data $DATA_PATH -symbol_representation "char2char" &
    wait
fi

# train
EPOCHS=13
MODEL_HYPERPARAMS=" -enc_layers 2 -dec_layers 2 -encoder_type brnn"
OPTIMIZER_HYPERPARAMS="-optim adam -learning_rate 0.001 -epochs $EPOCHS"

num_models=($(seq 1 1 $N))

TRAIN=false #true, false
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
TEST_FILE_SRC=$DATA_PATH/"$TEST_FILE_BASE"src.txt
TEST_FILE_TGT=$DATA_PATH/"$TEST_FILE_BASE"tgt.txt
BEAM=5

GENERATE=true #true, false
if [ "$GENERATE" = true ]
then
	printf "Generating texts for %s\n" "$TEST_FILE_BASE"
	TEST_FILE_SRC=$DATA_PATH/"$TEST_FILE_BASE"src.txt
	for NUM_MODEL in "${num_models[@]}"
	do
		TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$MODEL_NAME"_"$NUM_MODEL"_hypotheses.txt
		
		nohup python -u ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/"$MODEL_NAME"_"$NUM_MODEL".pt -src $TEST_FILE_SRC\
		 -output $TEST_FILE_TGT_HYPOTHESES -gpu 0 -max_length 395 -symbol_representation char2char -n_best 1 -beam_size $BEAM\
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

		bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh $TEST_FILE_TGT_HYPOTHESES character $TEST_FILE_TGT
	done
	wait
fi

# TODO fix
EVAL_ONE_HELDOUT_REFERENCE=true # true , false
declare -a eval_indices=( 41 18 0 39 40 25 28 3 32 10 )
if [ "$EVAL_ONE_HELDOUT_REFERENCE" = true ]
    then
    for MODEL_IDX in "${!model_sizes[@]}"
        do
        MODEL_NAME="${model_size_names[MODEL_IDX]}"
        MODEL_SIZE="${model_sizes[MODEL_IDX]}"
        for OPTIM_IDX in "${!optimizers[@]}"
            do
            OPTIM_NAME="${optimizer_names[OPTIM_IDX]}"
            OPTIMIZER="${optimizers[OPTIM_IDX]}"
            for NO_INPUT_RECORDS in "${number_of_input_records[@]}"
                do
                for NUM_MODEL_IDX in "${!num_models[@]}"
                    do
                    NUM_MODEL="${num_models[NUM_MODEL_IDX]}"
                    REF_FILE_IDX="${eval_indices[NUM_MODEL_IDX]}"
                    TEST_FILE_TGT="/home/users0/jagfelga/slu-work/NLG/E2E/human_as_prediction/""$REF_FILE_IDX"_references.txt
                    TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$BEAM"_"$MODEL_NAME"_"$OPTIM_NAME""$NUM_MODEL""$NO_INPUT_RECORDS"_hypotheses.txt
                    bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh $TEST_FILE_TGT_HYPOTHESES character $TEST_FILE_TGT
                done
            done
        done
    done

fi

deactivate
