#!/usr/bin/env bash

OUT_FILE=$1
MODE=$2 # character, word-delex, word
REF_FILE=$3
RELEXICALIZATION_FILE=${4:-none}

OUT_FILE_POSTPROCESSED=$OUT_FILE"_postprocessed"
EVAL_FILE=$OUT_FILE"_eval"

SCORING_SCRIPT="../../e2e-metrics/measure_scores.py"

if [[ $MODE = *"delex" ]]
    then
        python ../../data/postprocess_output.py $OUT_FILE $MODE $OUT_FILE_POSTPROCESSED --relexicalization_file $RELEXICALIZATION_FILE
    # nothing to do
    elif [ "$MODE" == "character" ]
        then
        OUT_FILE_POSTPROCESSED=$OUT_FILE
    # only detokenize for word and subword-based representation
    else
        python ../../data/postprocess_output.py $OUT_FILE $MODE $OUT_FILE_POSTPROCESSED
fi

# evaluate
ORIGINAL_LANG=$LANG
export LANG="en_US.UTF-8"
# upper/lower case is ignored in evaluation
python $SCORING_SCRIPT $REF_FILE $OUT_FILE_POSTPROCESSED > $EVAL_FILE
export LANG=$ORIGINAL_LANG