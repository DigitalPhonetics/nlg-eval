#!/usr/bin/env bash

NLG_DIR="/home/users0/jagfelga/slu-work/NLG/"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
DIVERSITY_EVAL_SCRIPT="/mount/arbeitsdaten34/projekte/slu/glori/pytorch-generation/util/variation_measures.py"
DATA_PATH=$NLG_DIR"WebNLG/data_word_based_force_delex_src_property_split_camel_case/"

FILE_BASE="dev_multi_ref"
#TODO need tokenized but not delexicalized src file with property split camel case? or property does not matter?
SRC_FILE="WebNLG/data_word_based/"$FILE_BASE"_src.txt" #$DATA_PATH$FILE_BASE"_src.txt"
TRAIN_FILE=$DATA_PATH"train_tgt_word_delex+char.txt"
declare -a MODELS=("" 0 1 2 3 4 5 6 7 8)

OUTPUT=human #word_based, char_based, human
EXPT_PATH=$NLG_DIR"WebNLG/model_word_based_property_split_camel_case/"
MODEL="_default_adam"
if [ "$OUTPUT" = char_based ]
then
    EXPT_PATH=$NLG_DIR"WebNLG/model_character_based_property_split_camel_case/1/"
    MODEL="_5_default_bidir_adam"
elif [ "$OUTPUT" = human ]
    then
        EXPT_PATH=$NLG_DIR"WebNLG/human_as_prediction/diversity_eval/"
        declare -a MODELS=(0 1 2 3 4 5 6 7)
        MODEL="_human"
fi

OUT_PATH=$EXPT_PATH"diversity_eval_entropy/"
mkdir -p $OUT_PATH

source /mount/projekte/slu/Projects/glori/bin/tensorflow_1.0/bin/activate

for i in "${MODELS[@]}"
    do
    DIVERSITY_EVAL_RESULTS=$OUT_PATH$FILE_BASE$MODEL$i"_text_diversity.txt"
    #DIVERSITY_EVAL_SUMMARY=$OUT_PATH$FILE_BASE$MODEL$i"_text_diversity_summary.txt"
    #echo "" > $DIVERSITY_EVAL_SUMMARY
    if [ "$OUTPUT" = char_based ] || [ "$OUTPUT" = human ]
    then
        if [ "$OUTPUT" = char_based ]
        then
            PRED_FILE=$EXPT_PATH$FILE_BASE$MODEL$i"_hypotheses.txt"
        else
            PRED_FILE=$EXPT_PATH$i"_as_predictions.txt"
        fi
        # combine tokenized srcgenerated texts
        SRC_TGT_FILE=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses.txt"
        SRC_TGT_DELEX=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses_delex.txt"
        SRC_TGT_RELEX=$OUT_PATH$FILE_BASE$MODEL$i"_src+hypotheses_relex.txt"
        TGT_DELEX_TEXTS=$OUT_PATH$FILE_BASE$MODEL$i"_hypotheses_delex.txt"

        paste $SRC_FILE $PRED_FILE > $SRC_TGT_FILE

        # tokenize the targets and delexicalize
        #TODO need different approach for WebNLG
        python $NLG_EVAL_CODE_PATH/read_datasets.py $SRC_TGT_FILE preprocessed-webnlg --delexicalize --tokenize_src --tokenize_tgt --tokenize\
         --output_path $SRC_TGT_DELEX --relexicalization_file $SRC_TGT_RELEX

        # extract only the texts
        cut -f2 $SRC_TGT_DELEX > $TGT_DELEX_TEXTS
    else
        PRED_FILE=$EXPT_PATH$FILE_BASE$MODEL$i".txt"
        TGT_DELEX_TEXTS=$PRED_FILE
    fi

    # run diversity evaluation
    python $DIVERSITY_EVAL_SCRIPT $TGT_DELEX_TEXTS --comparison_file $TRAIN_FILE &> $DIVERSITY_EVAL_RESULTS &
done
wait

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