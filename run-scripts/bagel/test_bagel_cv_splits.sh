#!/usr/bin/env bash

BAGEL_CV_FOLDER="/home/users0/jagfelga/slu-work/NLG/BAGEL/cv_word_based_delex/"

# check that targets in each fold sum to 404
for fold in $BAGEL_CV_FOLDER/*; do
    TRAIN_TARGETS=`grep -v "^$" $fold/train_tgt.txt | wc -l`
    DEV_TARGETS=`grep -v "^$" $fold/dev_tgt.txt | wc -l`
    TEST_TARGETS=`grep -v "^$" $fold/test_tgt.txt | wc -l`
    TOTAL_TARGETS=$((TRAIN_TARGETS+DEV_TARGETS+TEST_TARGETS))

    echo $TOTAL_TARGETS "targets"
done

# check that one input only appears in train, dev, or test
for fold in $BAGEL_CV_FOLDER/*; do
    UNIQ_TRAIN_INPUTS=`sort $fold/train_src.txt | uniq | wc -l | cut -f1 -d' '`
    UNIQ_DEV_INPUTS=`sort $fold/dev_src.txt | uniq | wc -l | cut -f1 -d' '`
    UNIQ_TEST_INPUTS=`wc -l $fold/test_src.txt | cut -f1 -d' '`
    TOTAL_INPUTS=$((UNIQ_TRAIN_INPUTS+UNIQ_DEV_INPUTS+UNIQ_TEST_INPUTS))
    echo $TOTAL_INPUTS "unique added inputs"
    UNIQ_COLLECTIVE_INPUTS=`cat $fold/*_src.txt | sort | uniq | wc -l`
    echo $UNIQ_COLLECTIVE_INPUTS "unique collective inputs"
done


