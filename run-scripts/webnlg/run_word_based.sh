#!/usr/bin/env bash

OPENNMT_PATH="../../openNMT-py"
NLG_EVAL_CODE_PATH="../../data"
DATA_PATH="../../datasets/webnlg/preprocessed/word_based/"
EXPT_PATH="../../experiments/webnlg/word_based/"
MODEL_NAME="word_based"

mkdir -p $EXPT_PATH

N=${1:-1}
TEST_FILE_BASE=${2:-dev_multi_ref}"_"

num_models=($(seq 1 1 $N))

# preprocess data for OpenNMT-py
PREPROCESS=true # true, false
if [ "$PREPROCESS" = true ]
    then
    python $OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train_src.txt -train_tgt $DATA_PATH/train_tgt.txt\
     -src_seq_length 4000 -valid_src $DATA_PATH/dev_src.txt -valid_tgt $DATA_PATH/dev_tgt.txt\
      -tgt_seq_length 4000 -save_data $DATA_PATH/ &
    wait
fi

# train
EPOCHS=13
MODEL_HYPERPARAMS=" -enc_layers 2 -dec_layers 2"
OPTIMIZER_HYPERPARAMS="-optim adam -learning_rate 0.001 -epochs $EPOCHS"

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
    for NUM_MODEL in "${num_models[@]}"
	do
		TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$MODEL_NAME"_"$NUM_MODEL"_hypotheses.txt

		nohup python -u ${OPENNMT_PATH}/translate.py -model $EXPT_PATH/"$MODEL_NAME"_"$NUM_MODEL".pt -src $TEST_FILE_SRC\
		-output "$TEST_FILE_TGT_HYPOTHESES" -gpu 0 -max_length 69 -n_best 1 -beam_size $BEAM_SIZE \
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


# TODO fix
EVAL_ONE_HELDOUT_REFERENCE=false # true , false
declare -a eval_indices=(0 6 2 4 4 1 1 0 0 3)
if [ "$EVAL_ONE_HELDOUT_REFERENCE" = true ]
    then
    for NUM_MODEL_IDX in "${!num_models[@]}"
        do
        NUM_MODEL="${num_models[NUM_MODEL_IDX]}"
        REF_FILE_IDX="${eval_indices[NUM_MODEL_IDX]}"
        TEST_FILE_TGT="/home/users0/jagfelga/slu-work/NLG/WebNLG/human_as_prediction/""$REF_FILE_IDX"_references.txt
        TEST_FILE_TGT_HYPOTHESES=$EXPT_PATH/"$TEST_FILE_BASE""$CONFIG"$NUM_MODEL.txt_postprocessed
        TEST_FILE_TGT_HYPOTHESES_SINGLE_REF_REMOVED=$EXPT_PATH/"$TEST_FILE_BASE""$CONFIG""$NUM_MODEL"_single_ref_removed.txt_postprocessed
        sed '30d;34d;53d;59d;62d;68d;70d;72d;77d;78d;82d;83d;85d;88d;93d;95d;122d;125d;143d;155d;161d;175d;184d;187d;188d;191d;202d;204d;222d;231d;232d;239d;240d;243d;310d;326d;353d;356d;362d;365d;367d;434d;479d;490d;493d;648d;649d;687d;719d;739d;742d;778d;779d;854d;859d'\
         $TEST_FILE_TGT_HYPOTHESES &> $TEST_FILE_TGT_HYPOTHESES_SINGLE_REF_REMOVED
        bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh  "$TEST_FILE_TGT_HYPOTHESES_SINGLE_REF_REMOVED" character\
                     $TEST_FILE_TGT
    done
fi


