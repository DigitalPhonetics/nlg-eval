#!/usr/bin/env bash

TEMPLATE_SCRIPT_PATH="../../systems/"
DATA_PATH="../../datasets/e2e/preprocessed/template/"
# MODEL_NAME="word_based"

mkdir -p $DATA_PATH

TRAIN_INPUTS=../../datasets/e2e/train_template.csv
DEV_INPUTS=../../datasets/e2e/dev_template.csv

# get unique inputs from train and dev splits that contain 'eatType' attribute
echo "MR" > $TRAIN_INPUTS
grep "eatType" ../../datasets/e2e/trainset.csv | grep -oP ^\".*?\" | sort | uniq >> $TRAIN_INPUTS
echo "MR" > $DEV_INPUTS
grep "eatType" ../../datasets/e2e/devset.csv >> $DEV_INPUTS

# train data
python $TEMPLATE_SCRIPT_PATH/template_1.py $TRAIN_INPUTS test
python $TEMPLATE_SCRIPT_PATH/template_2.py $TRAIN_INPUTS test

cp "$TRAIN_INPUTS".predicted_1 "$TRAIN_INPUTS".predicted_1+2
tail -n +2 "$TRAIN_INPUTS".predicted_2 >> "$TRAIN_INPUTS".predicted_1+2

# dev data
python $TEMPLATE_SCRIPT_PATH/template_1.py $DEV_INPUTS test
python $TEMPLATE_SCRIPT_PATH/template_2.py $DEV_INPUTS test

cp "$DEV_INPUTS".predicted_1 "$DEV_INPUTS".predicted_1+2
tail -n +2 "$DEV_INPUTS".predicted_2 >> "$DEV_INPUTS".predicted_1+2

mkdir -p $DATA_PATH/template_1
mkdir -p $DATA_PATH/template_2
mkdir -p $DATA_PATH/template_1+2

python preprocess.py template #&> $DATA_PATH/statistics.txt

# double the training + dev data for _1 and _2 to have same size as _1+2

GENERATE=true # true, false
if [ "$GENERATE" = true ]
then
	cp $DATA_PATH/train_1_src.txt $DATA_PATH/train_1+1_src.txt
	cat $DATA_PATH/train_1_src.txt >> $DATA_PATH/train_1+1_src.txt
	cp $DATA_PATH/train_1_tgt.txt $DATA_PATH/train_1+1_tgt.txt
	cat $DATA_PATH/train_1_tgt.txt >> $DATA_PATH/train_1+1_tgt.txt
	cp $DATA_PATH/train_1_relex.txt $DATA_PATH/train_1+1_relex.txt
	cat $DATA_PATH/train_1_relex.txt >> $DATA_PATH/train_1+1_relex.txt
	cp $DATA_PATH/train_2_src.txt $DATA_PATH/train_2+2_src.txt
	cat $DATA_PATH/train_2_src.txt >> $DATA_PATH/train_2+2_src.txt
	cp $DATA_PATH/train_2_tgt.txt $DATA_PATH/train_2+2_tgt.txt
	cat $DATA_PATH/train_2_tgt.txt >> $DATA_PATH/train_2+2_tgt.txt
	cp $DATA_PATH/train_2_relex.txt $DATA_PATH/train_2+2_relex.txt
	cat $DATA_PATH/train_2_relex.txt >> $DATA_PATH/train_2+2_relex.txt
	#dev
	cp $DATA_PATH/dev_1_src.txt $DATA_PATH/dev_1+1_src.txt
	cat $DATA_PATH/dev_1_src.txt >> $DATA_PATH/dev_1+1_src.txt
	cp $DATA_PATH/dev_1_tgt.txt $DATA_PATH/dev_1+1_tgt.txt
	cat $DATA_PATH/dev_1_tgt.txt >> $DATA_PATH/dev_1+1_tgt.txt
	cp $DATA_PATH/dev_1_relex.txt $DATA_PATH/dev_1+1_relex.txt
	cat $DATA_PATH/dev_1_relex.txt >> $DATA_PATH/dev_1+1_relex.txt
	cp $DATA_PATH/dev_2_src.txt $DATA_PATH/dev_2+2_src.txt
	cat $DATA_PATH/dev_2_src.txt >> $DATA_PATH/dev_2+2_src.txt
	cp $DATA_PATH/dev_2_tgt.txt $DATA_PATH/dev_2+2_tgt.txt
	cat $DATA_PATH/dev_2_tgt.txt >> $DATA_PATH/dev_2+2_tgt.txt
	cp $DATA_PATH/dev_2_relex.txt $DATA_PATH/dev_2+2_relex.txt
	cat $DATA_PATH/dev_2_relex.txt >> $DATA_PATH/dev_2+2_relex.txt

	mv $DATA_PATH/*1+1*.txt $DATA_PATH/template_1
	for f in $DATA_PATH/template_1/*; do mv $f `echo $f | sed 's/_.+._/_/'` ; done &
	mv $DATA_PATH/*2+2*.txt $DATA_PATH/template_2
	for f in $DATA_PATH/template_2/*; do mv $f `echo $f | sed 's/_.+._/_/'` ; done &
	mv $DATA_PATH/*1+2*.txt $DATA_PATH/template_1+2
	for f in $DATA_PATH/template_1+2/*; do mv $f `echo $f | sed 's/_.+._/_/'` ; done &
fi