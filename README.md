# Introduction

This repository contains the code to reproduce the results of the
data-to-text natural language generation (NLG) experiments reported in
the [INLG 2018](https://inlg2018.uvt.nl/) paper
[Sequence-to-Sequence Models for Data-to-Text Natural Language Generation: Word- vs. Character-based Processing and Output Diversity](https://aclanthology.coli.uni-saarland.de/papers/W18-6529/w18-6529).

Two datastes from NLG challenges ([E2E](http://www.macs.hw.ac.uk/InteractionLab/E2E/)
and [WebNLG](http://webnlg.loria.fr/pages/challenge.html)) held in 2017
were used to train and evaluate  sequence-to-sequence (Seq2Seq)-based
NLG models using the library [OpenNMT-py](https://github.com/OpenNMT/OpenNMT-py).

If you use this code, please cite the paper as follows:

```
@inproceedings{Seq2SeqData2Text_Jagfeld_18,
author = {Jagfeld, Glorianna and Jenne, Sabrina and Vu, Ngoc Thang},
title = {{Sequence-to-Sequence Models for Data-to-Text Natural Language Generation: Word- vs. Character-based Processing and Output Diversity}},
booktitle = {Proceedings of the 11th International Natural Language Generation Conference (INLG)},
year = {2018},
doi = {10.18653/v1/w18-6529},
pages = {221--232}
}
```
# Requirements
The code is written for python 2.7, PyTorch version 0.3.0  and was run on GPUs with CUDA 9.1.

The following python packages are needed:

* pytorch 0.3.0.post4
* torchtext 0.2.3 (pip install torchtext==0.2.3)
* six (torchtext requirement)
* matplotlib 2.2.3 (needed for evaluation)
* scikit-image (needed for evaluation)
* regex 2018.11.22 (needed for evaluation)

# Train & evaluate models for the E2E dataset

Download the dataset from https://github.com/tuetschek/e2e-dataset/releases/download/v1.0.0/e2e-dataset.zip and
unpack it into the folder datasets/e2e.

## Word-based generation
 
### Preprocessing
To create the preprocessed training, development and test splits for word-based generation from within the folder run-scripts/e2e run:

```
preprocess.py word
```

This lowercases and tokenizes the inputs and references and replaces the values of the NAME and NEAR slots by placeholders.
The output is stored in dataset/e2e/preprocessed/word_based/.
 
##### Example input-reference pair for word-based processing:

* input: name [ NAME-X ] , eattype [ coffee shop ] , food [ italian ] , pricerange [ less than £20 ] , customer rating [ low ] ,
 area [ riverside ] , familyfriendly [ yes ] , near [ NEAR-X ]
* reference: NAME-X is an inexpensive coffee shop near NEAR-X and the river . it is family-friendly and serves pasta .
 
### Training, generation and automatic evaluation
To train N models with different random seeds in paralell, and subsequently
generate texts for the development set and compute automatic evaluation metrics
from within the folder run-scripts/e2e run:

```
run_word_based.sh N
```

To generate texts and evaluate on the test set run

```
run_word_based.sh N test
```

Consult the bash script to activate/deactivate the individual steps of data preprocessing for OpenNMT-py, training, generation and evaluation.
 
Running all steps produces the following files in the folder experiments/e2e/word_based,
where n ϵ (1 ... N):

- train_word_based_n.log: training log file 
- word_based_n.pt: trained model
- generate_{dev/test}_multi_ref_word_based_n.log: generation log file
- {dev/test}_multi_ref_word_based_n_hypotheses.txt: delexicalized generated texts (one best hypothesis per input)
- {dev/test}_multi_ref_word_based_n_hypotheses.txt_postprocessed: lexicalized generated texts
- {dev/test}_multi_ref_word_based_n_hypotheses.txt_eval: evaluation file (see example below)

 
##### Example evaluation results (_eval file) on the development set:
 
SCORES:\
\==========\
BLEU: 0.7310\
NIST: 8.8055\
METEOR: 0.4803\
ROUGE_L: 0.7551\
CIDEr: 2.3788
 
## Character-based generation

### Preprocessing
To create the preprocessed training, development and test splits for character-based generation from within the folder run-scripts/e2e run:

```
preprocess.py character
```

This only lowercases the inputs and references.
The output is stored in dataset/e2e/preprocessed/character_based/.
 
##### Example input-reference pair for character-based processing:
* input: name[the eagle],eattype[coffee shop],food[italian],pricerange[less than £20],customer rating[low],area[riverside],familyfriendly[yes],near[burger king]

* reference: the eagle is an inexpensive coffee shop near burger king and the river. it is family-friendly and serves pasta.
 
### Training, generation and automatic evaluation
Training, generation and evaluation works analogously to the word-based models but instead use the script run_character_based.sh.

##### Example evaluation results (_eval file) on the development set:
SCORES:\
\==============\
BLEU: 0.7103\
NIST: 8.7457\
METEOR: 0.4706\
ROUGE_L: 0.7354\
CIDEr: 2.2999

# Train & evaluate models for the WebNLG dataset

Download the dataset from https://gitlab.com/shimorina/webnlg-dataset/tree/master/release_v2/xml and place the train, dev, test folder with subfolders containing XML files from webnlg-dataset-master/release_v2/xml/ in the folder
 datasets/webnlg.
To obtain single files for the training, development and test split from the folder run-scripts/webnlg run

```
bash preprocess_to_single_files.sh
```

This will create a single file for each split of the dataset in the folder datasets/webnlg,
train.txt, dev.txt, test.txt, that each contain one input and reference per line.
Inputs with multiple references are duplicated for each refrence.

## Word-based generation
### Preprocessing
To create the preprocessed training, development and test splits for word-based generation from within the folder run-scripts/webnlg run:

```
python preprocess.py word
```

The output is stored in dataset/webnlg/preprocessed/word_based/.
This splits entity and property names at camel case, lowercases the inputs and references, delexicalizes all entities
in the inputs and also in the references (if an input entity appears verbatim in the reference).
For more details about the delexicalization consult Section 4 of the [paper](https://arxiv.org/pdf/1810.04864.pdf).

##### Example input-reference pair for word-based processing:

* input: capital ( BRIDGE-0 [ PATIENT-0 ] ) , material ( AGENT-0 [ PATIENT-1 ] ) , leader title ( BRIDGE-0 [ PATIENT-2 ] ) , dedicated to ( AGENT-0 [ PATIENT-3 ] ) , location ( AGENT-0 [ BRIDGE-0 ] ) , designer ( AGENT-0 [ PATIENT-4 ] ) , legislature ( BRIDGE-0 [ PATIENT-5 ] )
* reference: huyseyin butuner and hilmi guner designed the AGENT-0 . it is located in PATIENT-0 , BRIDGE-0 , which has legislature of national assembly , and led by the prime minster . the memorial is made from PATIENT-1 , and is dedicated to the PATIENT-3 .
### Training, generation and automatic evaluation
Training, generation and evaluation works analogously to the E2E models
but use the script run_word_based.sh from the folder run-scripts/webnlg.

##### Example evaluation results on the development set:
SCORES:\
\========\
BLEU: 0.4806\
NIST: 9.2032\
METEOR: 0.3705\
ROUGE_L: 0.6450\
CIDEr: 3.3558

## Character-based generation
### Preprocessing
To create the preprocessed training, development and test splits for
character-based generation from within the folder run-scripts/webnlg run:

```
python preprocess.py character
```

This splits entity and property names at camel case and lowercases the inputs and references.
The output is stored in dataset/webnlg/preprocessed/character_based/.

##### Example input-reference pair for character-based processing:
* input: capital(azerbaijan[baku]),material(baku turkish martyrs' memorial[red granite and white marble]),leader title(azerbaijan[prime minister of azerbaijan]),dedicated to(baku turkish martyrs' memorial[ottoman army soldiers killed in the battle of baku]),location(baku turkish martyrs' memorial[azerbaijan]),designer(baku turkish martyrs' memorial[hüseyin bütüner and hilmi güner]),legislature(azerbaijan[national assembly (azerbaijan)])
* reference: huyseyin butuner and hilmi guner designed the baku turkish martyrs' memorial. it is located in baku, azerbaijan, which has legislature of national assembly, and led by the prime minster. the memorial is made from red granite and white marble, and is dedicated to the ottoman army soldiers killed in the battle of baku.

### Training, generation and automatic evaluation
Training, generation and evaluation works analogously to the E2E models
but use the script run_character_based.sh from the folder run-scripts/webnlg.

##### Example evaluation results on the development set:
SCORES:\
\========\
BLEU: 0.5737\
NIST: 9.5549\
METEOR: 0.4020\
ROUGE_L: 0.7151\
CIDEr: 3.6612

# Template Experiment

We generate synthetic training data based on two templates using the scripts systems/template_1.py and systems/template_2.py.
Template~1 corresponds to [UKP-TUDA's submission to the E2E challenge](https://github.com/UKPLab/e2e-nlg-challenge-2017/blob/master/components/template-baseline.py),
where the order of describing the input information is fixed.
Specifically, the restaurant's customer rating is always mentioned before its location.
For Template~2, we change the the beginning of the template and switch the order of mentioning the rating and location of the restaurant.

To generate the training, development and test data using the two templates, from the folder run-scripts/e2e/ raun:

```
bash create_template_data.sh
```

To train N models on the data created with template 1, template 2 or
both templates, from the folder run-scripts/e2e/ run

```
bash run_template_experiment.sh N TEMPLATE_NUMBER
```

where TEMPLATE_NUMBER is either 1, 2 or 1+2.

The texts are generated for the 10 random test set inputs we evaluated on
for the results discussed in Section 7 and Table 7 of the paper.
They can be found in the file datasets/e2e/test_template_10_random_inputs.txt.

