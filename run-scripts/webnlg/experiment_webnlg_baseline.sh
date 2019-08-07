#!/usr/bin/env bash

source /home/users0/jagfelga/slu-glori/bin/torch_0.2/bin/activate

# reproduce WebNLG baseline, adapted from http://webnlg.loria.fr/pages/baseline.html

OPENNMT_PATH="/home/users0/jagfelga/slu-work/OpenNMT-py"
NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"
CORPUS_PATH="/home/users0/jagfelga/slu-work/WebNLG/data_original/"
DATA_PATH="/home/users0/jagfelga/slu-work/NLG/WebNLG/data_challenge_baseline_preprocessed/"
EXPT_PATH="/home/users0/jagfelga/slu-work/NLG/WebNLG/model_challenge_baseline/"
WEBNLG_BASELINE_CODE_PATH="/home/users0/jagfelga/slu-work/webnlg-baseline"
WEBNLG_ORIGINAL_DATA="/home/users0/jagfelga/slu-work/WebNLG/data_original/"

# data preprocessing
#~/slu-work/webnlg-baseline$ python3 $WEBNLG_BASELINE_CODE_PATH/webnlg_baseline_input.py -i $WEBNLG_ORIGINAL_DATA

#mv *.triple ~/slu-work/WebNLG/data_challenge_baseline_preprocessed
#mv *.lex ~/slu-work/WebNLG/data_challenge_baseline_preprocessed

#$OPENNMT_PATH/preprocess.py -train_src $DATA_PATH/train-webnlg-all-delex.triple -train_tgt $DATA_PATH/train-webnlg-all-delex.lex -valid_src $DATA_PATH/dev-webnlg-all-delex.triple -valid_tgt $DATA_PATH/dev-webnlg-all-delex.lex -src_seq_length 70 -tgt_seq_length 70 -save_data $DATA_PATH

# * tgt vocab size: 5032.
# * src vocab size: 1318.
# 18095 train examples (originally 18101, so 6 instances were removed - probably too long)

# train
#nohup python -u $OPENNMT_PATH/train.py -data $DATA_PATH -save_model $EXPT_PATH -gpuid 0 >& $EXPT_PATH/train.log &

wait

# test on dev data
#nohup python -u $OPENNMT_PATH/translate.py -model $EXPT_PATH/_acc_*_e13.pt -src $DATA_PATH/dev-webnlg-all-delex.triple -output $EXPT_PATH/dev_e13.txt >& $EXPT_PATH/test_dev_e13.log &

wait

# relexicalize
python3 $WEBNLG_BASELINE_CODE_PATH/webnlg_relexicalise.py -i $WEBNLG_ORIGINAL_DATA -f $EXPT_PATH/dev_e13.txt
# evaluate

#bash $NLG_EVAL_CODE_PATH/run-scripts/webnlg/evaluate.sh $EXPT_PATH/test_e13.txt character

deactivate