import sys
from os import path

# add NLGevaluation main directory to modules path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import NLGevaluation.data.dataset_bagel
#from NLGevaluation.util import arguments

#import NLGevaluation.data.args
#import NLGevaluation.data.read_datasets

# https://github.com/shawnwun/RNNLG/data/original/restaurant
dataset_path = "/home/users0/jagfelga/slu-work/corpora/Bagel_NLG/train+test.txt"
processed_datasets_directory = "/home/users0/jagfelga/slu-work/NLG/BAGEL/"
dataset_type = "bagel"
entities_to_delexicalize = [] #.split(",")
#print "%d entities to delexicalize: %s" %(len(entities_to_delexicalize), sorted(entities_to_delexicalize))

log_level = "info"

# word based, delexicalized: lowercase, tokenize, delexicalize
# word based, not delexicalized: lowercase, tokenize
# char based: none of the three

def group_instances_delexicalized():
    processed_dataset_subdirectory = processed_datasets_directory + "/cv_word_based_delex/"
    lowercase = True
    tokenize = True
    delexicalize = True

    dataset = NLGevaluation.data.dataset_bagel.BAGELDataset(delexicalize, lowercase, tokenize)
    dataset.read_from_file(dataset_path)

    dataset.write_cross_validation_files(processed_dataset_subdirectory, 10)

def group_instances():
    processed_dataset_subdirectory = processed_datasets_directory + "/cv_word_based/"
    tokenize =True
    lowercase = True
    delexicalize = False

    dataset = NLGevaluation.data.dataset_bagel.BAGELDataset(delexicalize, lowercase, tokenize)
    dataset.read_from_file(dataset_path)

    dataset.write_cross_validation_files(processed_dataset_subdirectory, 10)

def group_instances_character_based():
    processed_dataset_subdirectory = processed_datasets_directory + "/cv_char_based/"
    tokenize =False
    lowercase = False
    delexicalize = False

    dataset = NLGevaluation.data.dataset_bagel.BAGELDataset(delexicalize, lowercase, tokenize)
    dataset.read_from_file(dataset_path)

    dataset.write_cross_validation_files(processed_dataset_subdirectory, 10)



if __name__ =="__main__":
    group_instances_delexicalized()
    #group_instances_character_based()
    #group_instances()