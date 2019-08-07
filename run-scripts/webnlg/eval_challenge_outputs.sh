#!/usr/bin/env bash

CHALLENGE_OUTPUTS_FOLDER="/home/users0/jagfelga/slu-work/WebNLG/challenge_submission_outputs/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/WebNLG/data_character_based_property_split_camel_case/"
EVAL_SCRIPT=/home/users0/jagfelga/slu-work/NLG/NLGevaluation/run-scripts/evaluate.sh

for FOLDER in $CHALLENGE_OUTPUTS_FOLDER/*/;
    do
    head -n 971 $FOLDER/test_predictions.txt > $FOLDER/test_seen_predictions.txt
    tail -n 891 $FOLDER/test_predictions.txt > $FOLDER/test_unseen_predictions.txt
done

# evaluate
REF_ALL=$DATA_PATH/test_tgt.txt
REF_SEEN=$DATA_PATH/test_seen_categories_tgt.txt
REF_UNSEEN=$DATA_PATH/test_unseen_categories_tgt.txt

for FOLDER in $CHALLENGE_OUTPUTS_FOLDER/*/;
    do
    PRED_ALL=$FOLDER/test_predictions.txt
    PRED_SEEN=$FOLDER/test_seen_predictions.txt
    PRED_UNSEEN=$FOLDER/test_unseen_predictions.txt
    bash $EVAL_SCRIPT $PRED_ALL character $REF_ALL &
    bash $EVAL_SCRIPT $PRED_SEEN character $REF_SEEN &
    bash $EVAL_SCRIPT $PRED_UNSEEN character $REF_UNSEEN &
done
