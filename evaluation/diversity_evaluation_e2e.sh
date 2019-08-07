#!/usr/bin/env bash

NLG_DIR="/home/users0/jagfelga/slu-work/NLG/"
NLG_EVAL_CODE_PATH=$NLG_DIR"NLGevaluation/data/"
DIVERSITY_EVAL_SCRIPT="/mount/arbeitsdaten34/projekte/slu/glori/pytorch-generation/util/variation_measures.py"
DATA_PATH=$NLG_DIR"E2E/data_word_based_delex/"
FILE_BASE="dev_multi_ref"
SRC_FILE=$NLG_DIR"E2E/data_word_based/"$FILE_BASE"_src.txt"
TRAIN_FILE=$DATA_PATH"train_tgt_word_delex+char.txt"

OUTPUT=char_based #word_based, char_based, human
EXPT_PATH=$NLG_DIR"E2E/model_word_based_delex/5/"
declare -a MODELS=("" 0 1 2 3 4 5 6 7 8)
MODEL="_15_small_sgd"
if [ "$OUTPUT" = char_based ]
then
    EXPT_PATH=$NLG_DIR"E2E/model_character_based/8/"
    declare -a MODELS=("" 1 2 3 4 5 6 7 8 9)
    MODEL="_5_default_bidir_adam"
elif [ "$OUTPUT" = human ]
    then
        EXPT_PATH=$NLG_DIR"E2E/human_as_prediction/"
        declare -a MODELS=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42)
        MODEL="_human"
fi

OUT_PATH=$EXPT_PATH"diversity_eval_entropy/"
mkdir -p $OUT_PATH

source /mount/projekte/slu/Projects/glori/bin/tensorflow_1.0/bin/activate

COMPUTE_DIVERSITY_STATISTICS=false # true, false
if [ "$COMPUTE_DIVERSITY_STATISTICS" = true ]
    then
    for i in "${MODELS[@]}"
        do
        if [ "$OUTPUT" = human ]
        then
            PRED_FILE=$EXPT_PATH$i"_as_predictions.txt"
        else
            PRED_FILE=$EXPT_PATH$FILE_BASE$MODEL$i"_hypotheses.txt"
        fi
        DIVERSITY_EVAL_RESULTS=$OUT_PATH$FILE_BASE$MODEL$i"_text_diversity.txt"
        #DIVERSITY_EVAL_SUMMARY=$OUT_PATH$FILE_BASE$MODEL$i"_text_diversity_summary.txt"
        #echo "" > $DIVERSITY_EVAL_SUMMARY
        if [ "$OUTPUT" = char_based ] || [ "$OUTPUT" = human ]
        then
            # combine tokenized src with generated texts
            SRC_TGT_FILE=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses.txt"
            SRC_TGT_DELEX=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses_delex.txt"
            SRC_TGT_RELEX=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses_relex.txt"
            TGT_DELEX_TEXTS=$OUT_PATH$FILE_BASE$MODEL$i"_hypotheses_delex.txt"

            paste $SRC_FILE $PRED_FILE > $SRC_TGT_FILE

            # tokenize the targets and delexicalize
            python $NLG_EVAL_CODE_PATH/read_datasets.py $SRC_TGT_FILE preprocessed --delexicalize --tokenize\
             --output_path $SRC_TGT_DELEX --relexicalization_file $SRC_TGT_RELEX --entities_to_delexicalize name near

            # extract only the texts
            cut -f2 $SRC_TGT_DELEX > $TGT_DELEX_TEXTS

        else
            TGT_DELEX_TEXTS=$PRED_FILE
        fi

        # run diversity evaluation
        python $DIVERSITY_EVAL_SCRIPT $TGT_DELEX_TEXTS --comparison_file $TRAIN_FILE &> $DIVERSITY_EVAL_RESULTS &
        wait

        # extract relevant info
        #grep "model-1 uniq 1 grams" $DIVERSITY_EVAL_RESULTS >> $DIVERSITY_EVAL_SUMMARY
        #grep "model-1 uniq sentences" $DIVERSITY_EVAL_RESULTS >> $DIVERSITY_EVAL_SUMMARY
        #grep "model-1 uniq texts" $DIVERSITY_EVAL_RESULTS >> $DIVERSITY_EVAL_SUMMARY
        #grep "of model-1 not in model-2" $DIVERSITY_EVAL_RESULTS >> $DIVERSITY_EVAL_SUMMARY
    done
    wait
fi

# meta file - aggregate the stats of all summary files
DIVERSITY_EVAL_SUMMARY=$OUT_PATH$FILE_BASE$MODEL"_text_diversity_summary.txt"
grep "model-1 uniq texts" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" > $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "model-1 uniq sentences" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY

grep "model-1 text entropy for up to 1-grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "model-1 text entropy for up to 2-grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "model-1 text entropy for up to 3-grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "model-1 text entropy for up to 4-grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "model-1 text entropy for up to 5-grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY

grep "model-1 uniq 1 grams" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "texts of model-1 not in model-2" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "sentences of model-1 not in model-2" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY
grep "words of model-1 not in model-2" $OUT_PATH$FILE_BASE$MODEL*"_text_diversity.txt" >> $DIVERSITY_EVAL_SUMMARY
printf '\n\n\n\n' >> $DIVERSITY_EVAL_SUMMARY