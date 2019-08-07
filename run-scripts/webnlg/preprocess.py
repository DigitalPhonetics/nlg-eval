import sys
from os import path, makedirs
import argparse

# add NLGevaluation main directory to modules path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import NLGevaluation.data.read_datasets
from NLGevaluation.util import arguments

dataset_directory = "../../datasets/webnlg/"
processed_datasets_directory = "../../datasets/webnlg/preprocessed/"
dataset_type = "webnlg"

lowercase = True

only_source = False
multi_reference = False
collect_multi_references = False
entities_to_delexicalize = []

log_level = "info"


def preprocess_data_multi_ref(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize=True, separate_inputs_for_number_of_records=False):
    if tokenize:
        record_delimiter = " , "
    else:
        record_delimiter = ","
    preprocess_data(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                    group_inputs=True, tokenize=tokenize, record_delimiter=record_delimiter,
                    separate_inputs_for_number_of_records=separate_inputs_for_number_of_records)


def preprocess_data_single_ref(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize=True, separate_inputs_for_number_of_records=False):
    if tokenize:
        record_delimiter = " , "
    else:
        record_delimiter = ","
    preprocess_data(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                    group_inputs=False, tokenize=tokenize, record_delimiter=record_delimiter,
                    separate_inputs_for_number_of_records=separate_inputs_for_number_of_records)


def preprocess_data(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping, group_inputs,
                    tokenize, record_delimiter, separate_inputs_for_number_of_records):
    processed_dataset_subdirectory = processed_datasets_directory + output_folder
    dataset_path = dataset_directory + input_file
    output_path = processed_dataset_subdirectory + output_name

    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs, collect_multi_references, entities_to_delexicalize, log_level,
                                     record_delimiter=record_delimiter,
                                     separate_inputs_for_number_of_records=separate_inputs_for_number_of_records)

    NLGevaluation.data.read_datasets.process_dataset(args)


def prepare_word_based_delex_experiment():
    output_folder = "word_based/"

    full_path_to_output_folder = processed_datasets_directory + output_folder

    if not path.exists(full_path_to_output_folder):
        makedirs(full_path_to_output_folder)

    delexicalize = True
    delexicalize_after_grouping = False
    preprocess_data_single_ref("train.txt", "train", output_folder, delexicalize, delexicalize_after_grouping)
    preprocess_data_single_ref("dev.txt", "dev", output_folder, delexicalize, delexicalize_after_grouping)

    delexicalize = False
    delexicalize_after_grouping = True
    preprocess_data_multi_ref("dev.txt", "dev_multi_ref", output_folder, delexicalize, delexicalize_after_grouping)
    preprocess_data_multi_ref("test.txt", "test", output_folder, delexicalize, delexicalize_after_grouping)

    # lexicalized reference files for evaluation
    delexicalize_after_grouping = False
    preprocess_data_multi_ref("dev.txt", "dev_multi_ref_lexicalized", output_folder, delexicalize, delexicalize_after_grouping)
    preprocess_data_multi_ref("test.txt", "test_lexicalized", output_folder, delexicalize, delexicalize_after_grouping)


def prepare_character_based_experiment():
    output_folder = "character_based/"

    full_path_to_output_folder = processed_datasets_directory + output_folder

    if not path.exists(full_path_to_output_folder):
        makedirs(full_path_to_output_folder)

    delexicalize = False
    delexicalize_after_grouping = False
    tokenize = False

    preprocess_data_single_ref("train.txt", "train", output_folder, delexicalize, delexicalize_after_grouping, tokenize)
    preprocess_data_single_ref("dev.txt", "dev", output_folder, delexicalize, delexicalize_after_grouping, tokenize)

    preprocess_data_multi_ref("dev.txt", "dev_multi_ref", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize)
    preprocess_data_multi_ref("test.txt", "test", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["word", "character", "template-word"])

    args = parser.parse_args()

    if args.mode == "character":
        prepare_character_based_experiment()

    elif args.mode == "word":
        prepare_word_based_delex_experiment()

    elif args.mode == "template-word":
        prepare_template_word_delex_experiment()
