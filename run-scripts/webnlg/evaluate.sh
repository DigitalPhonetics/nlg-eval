#!/usr/bin/env bash

#!/usr/bin/env bash

OUT_FILE=$1
MODE=$2 # character, word-delex, word
REF_FILE=$3
RELEXICALIZATION_FILE=$4

#REF_FILE=/home/users0/jagfelga/slu-work/NLG/WebNLG/dev_tgt.txt
REF_FILE=/home/users0/jagfelga/slu-work/NLG/WebNLG/test_tgt.txt
RELEXICALIZATION_FILE=/home/users0/jagfelga/slu-work/NLG/WebNLG/data_word_based_delex/test_relex.txt

OUT_FILE_POSTPROCESSED=$OUT_FILE"_postprocessed"
EVAL_FILE=$OUT_FILE"_eval"

SCORING_SCRIPT="/home/users0/jagfelga/slu-work/E2ENLG/e2e-metrics/measure_scores.py"


python /home/users0/jagfelga/slu-work/NLG/code/data/postprocess_output.py $OUT_FILE $MODE\
        $OUT_FILE_POSTPROCESSED --relexicalization_file $RELEXICALIZATION_FILE

# remove empty lines if there are any
grep -v "^$" $OUT_FILE_POSTPROCESSED > $OUT_FILE_POSTPROCESSED"_no_empty"
mv $OUT_FILE_POSTPROCESSED"_no_empty" $OUT_FILE_POSTPROCESSED

# evaluate
export LANG="en_US.UTF-8"
# upper/lower case is ignored in evaluation
python $SCORING_SCRIPT $REF_FILE $OUT_FILE_POSTPROCESSED > $EVAL_FILE
export LANG="de_DE.UTF-8"