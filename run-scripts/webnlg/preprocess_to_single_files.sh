# obtain WebNLG dataset splits in a single file each (train.txt, dev.txt, test.txt)

PREPROCESSING_SCRIPT="../../data/webnlg/" #preprocess_webnlg.py
DATASET_DIRECTORY="../../datasets/webnlg/"

python "$PREPROCESSING_SCRIPT"preprocess_webnlg.py "$DATASET_DIRECTORY"/train/ "$DATASET_DIRECTORY"/train singleref &
python "$PREPROCESSING_SCRIPT"preprocess_webnlg.py "$DATASET_DIRECTORY"/dev/ "$DATASET_DIRECTORY"/dev singleref &
python "$PREPROCESSING_SCRIPT"preprocess_webnlg.py "$DATASET_DIRECTORY"/test/ "$DATASET_DIRECTORY"/test singleref &