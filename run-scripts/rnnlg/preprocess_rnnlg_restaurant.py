import sys
from os import path
# add NLGevaluation main directory to modules path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import NLGevaluation.data.read_datasets
from NLGevaluation.util import arguments

#import NLGevaluation.data.args
#import NLGevaluation.data.read_datasets

# https://github.com/shawnwun/RNNLG/data/original/restaurant
dataset_directory = "/home/users0/jagfelga/slu-work/RNNLG/data/original/restaurant/"
processed_datasets_directory = "/home/users0/jagfelga/slu-work/NLG/RNNLG-Restaurant/"
dataset_type = "rnnlg"
entities_to_delexicalize = "address,area,count,food,good_for_meal,goodformeal," \
                           "name,near,phone,postcode,price,pricerange,price_range,type".split(",")
lowercase = True
tokenize = True

only_source = False
multi_reference = False

log_level = "info"

def prepare_word_based_delex_experiment():
    processed_dataset_subdirectory = processed_datasets_directory + "data_word_based_delex/"
    dataset_path = dataset_directory + "train.json"
    output_path = processed_dataset_subdirectory + "train"
    delexicalize = True
    delexicalize_after_grouping = False
    group_inputs = False
    collect_multi_references = False
    #TODO add additional normalization from https://github.com/shawnwun/RNNLG/utils/nlp.py/normalize?

    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     collect_multi_references,
                                     group_inputs, entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    # development data
    dataset_path = dataset_directory + "valid.json"
    output_path = processed_dataset_subdirectory + "dev"
    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     collect_multi_references,
                                     group_inputs, entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    # test data
    dataset_path = dataset_directory + "test.json"
    output_path = processed_dataset_subdirectory + "test"
    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     collect_multi_references,
                                     group_inputs, entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

def prepare_word_based_experiment():
    processed_dataset_subdirectory = processed_datasets_directory + "data_word_based/"
    delexicalize = False
    delexicalize_after_grouping = False
    group_inputs = False
    collect_multi_references = False

    dev_dataset_path = dataset_directory + "train.json"
    dev_output_path = processed_dataset_subdirectory + "train"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    collect_multi_references = True
    # development data multi-ref
    dev_dataset_path = dataset_directory + "valid.json"
    dev_output_path = processed_dataset_subdirectory + "dev_multi_ref"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    # test data multi-ref
    dev_dataset_path = dataset_directory + "test.json"
    dev_output_path = processed_dataset_subdirectory + "test_multi_ref"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

def prepare_character_based_experiment():
    processed_dataset_subdirectory = processed_datasets_directory + "data_character_based/"
    lowercase = True # the whole dataset is lowercased except for some probably erroneous examples in the dev set
    # lowercase it also for character based to be consistent
    tokenize = False
    delexicalize = False
    delexicalize_after_grouping = False
    group_inputs = False
    collect_multi_references = False

    dev_dataset_path = dataset_directory + "train.json"
    dev_output_path = processed_dataset_subdirectory + "train"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    # development data - single reference
    dataset_path = dataset_directory + "valid.json"
    output_path = processed_dataset_subdirectory + "dev"
    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     collect_multi_references,
                                     group_inputs, entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    collect_multi_references = True
    # development data multi-ref
    dev_dataset_path = dataset_directory + "valid.json"
    dev_output_path = processed_dataset_subdirectory + "dev_multi_ref"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

    # test data multi-ref
    dev_dataset_path = dataset_directory + "test.json"
    dev_output_path = processed_dataset_subdirectory + "test_multi_ref"
    args = arguments.DatsetArguments(dev_dataset_path, dataset_type, dev_output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs,
                                     collect_multi_references,
                                     entities_to_delexicalize, log_level)

    NLGevaluation.data.read_datasets.process_dataset(args)

if __name__ =="__main__":
    prepare_word_based_delex_experiment()

    #prepare_word_based_experiment()

    #prepare_character_based_experiment()