import sys
from os import path, makedirs
import argparse

# add NLGevaluation main directory to modules path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import NLGevaluation.data.read_datasets
from NLGevaluation.util import arguments



dataset_directory = "../../datasets/e2e/"
processed_datasets_directory = "../../datasets/e2e/preprocessed/"
dataset_type = "e2e"

entities_to_delexicalize = "name,near".split(",")

lowercase = True

only_source = False
multi_reference = False
collect_multi_references = False

log_level = "info"


def preprocess_data_multi_ref(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize=True, lowercase=True, randomize_record_order=False, record_delimiter=" , ",
                              flatten_records=False,
                              separate_inputs_for_number_of_records=False):
    dataset_path = dataset_directory + input_file
    preprocess_data(dataset_path, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                    True, tokenize, lowercase, randomize_record_order, record_delimiter, flatten_records,
                    separate_inputs_for_number_of_records)


def preprocess_data_single_ref(input_file, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize=True, lowercase=True, randomize_record_order=False, record_delimiter=" , ",
                               flatten_records=False, separate_inputs_for_number_of_records=False):
    dataset_path = dataset_directory + input_file
    preprocess_data(dataset_path, output_name, output_folder, delexicalize, delexicalize_after_grouping,
                    False, tokenize, lowercase, randomize_record_order, record_delimiter, flatten_records,
                    separate_inputs_for_number_of_records=separate_inputs_for_number_of_records)


def preprocess_data(dataset_path, output_name, output_folder, delexicalize, delexicalize_after_grouping, group_inputs,
                    tokenize, lowercase, randomize_record_order, record_delimiter, flatten_records,
                    separate_inputs_for_number_of_records, tokenize_src=None, tokenize_tgt=None):
    processed_dataset_subdirectory = processed_datasets_directory + output_folder
    output_path = processed_dataset_subdirectory + output_name

    if not tokenize_src:
        tokenize_src = tokenize
    if not tokenize_tgt:
        tokenize_tgt = tokenize

    args = arguments.DatsetArguments(dataset_path, dataset_type, output_path,
                                     only_source, multi_reference, lowercase, tokenize,
                                     delexicalize, delexicalize_after_grouping,
                                     group_inputs, collect_multi_references, entities_to_delexicalize, log_level,
                                     randomize_record_order, record_delimiter, flatten_records,
                                     separate_inputs_for_number_of_records, tokenize_src, tokenize_tgt)

    NLGevaluation.data.read_datasets.process_dataset(args)


def prepare_template_word_delex_experiment():
    output_folder = "template/"

    full_path_to_output_folder = processed_datasets_directory + output_folder

    if not path.exists(full_path_to_output_folder):
        makedirs(full_path_to_output_folder)

    delexicalize = True
    delexicalize_after_grouping = False
    tokenize = True

    #dataset_path = processed_datasets_directory + "/data_template/"

    # single ref
    for t in ["1", "2", "1+2"]:
        preprocess_data(dataset_directory + "/train_template.csv.predicted_%s" % t, "train_%s" % t, output_folder, delexicalize,
                    delexicalize_after_grouping, False, tokenize, lowercase, randomize_record_order=False,
                       record_delimiter=" , ", flatten_records=False, separate_inputs_for_number_of_records=False)
        preprocess_data(dataset_directory + "/dev_template.csv.predicted_%s" % t, "dev_%s" % t, output_folder, delexicalize,
                       delexicalize_after_grouping, False, tokenize, lowercase, randomize_record_order=False,
                       record_delimiter=" , ", flatten_records=False, separate_inputs_for_number_of_records=False)
        #preprocess_data(dataset_path + "test_uniq_src.txt.predicted_%s" % t, "test_%s" % t, output_folder, delexicalize,
        #                delexicalize_after_grouping, False, tokenize, lowercase, randomize_input_order,
        #                record_delimiter=" , ", flatten_records=False, separate_inputs_for_number_of_records=False)


def prepare_word_based_delex_experiment():
    output_folder = "word_based/"

    full_path_to_output_folder = processed_datasets_directory + output_folder

    if not path.exists(full_path_to_output_folder):
        makedirs(full_path_to_output_folder)

    delexicalize = True
    delexicalize_after_grouping = False
    tokenize = True

    preprocess_data_single_ref("trainset.csv", "train", output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize, lowercase)
    preprocess_data_single_ref("devset.csv", "dev", output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize, lowercase)

    delexicalize = False
    delexicalize_after_grouping = True

    preprocess_data_multi_ref("devset.csv", "dev_multi_ref", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase)
    preprocess_data_multi_ref("testset_w_refs.csv", "test", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase)

    # lexicalized reference files for evaluation
    delexicalize_after_grouping = False
    preprocess_data_multi_ref("devset.csv", "dev_multi_ref_lexicalized", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase)
    preprocess_data_multi_ref("testset_w_refs.csv", "test_lexicalized", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase)


def prepare_character_based_experiment():
    output_folder = "character_based/"

    full_path_to_output_folder = processed_datasets_directory + output_folder

    if not path.exists(full_path_to_output_folder):
        makedirs(full_path_to_output_folder)

    delexicalize = False
    delexicalize_after_grouping = False
    tokenize = False
    randomize_input_order = False
    record_delimiter = ","

    lowercase = True

    preprocess_data_single_ref("trainset.csv", "train", output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize, lowercase, randomize_input_order, record_delimiter)
    preprocess_data_single_ref("devset.csv", "dev", output_folder, delexicalize, delexicalize_after_grouping,
                               tokenize, lowercase, randomize_input_order, record_delimiter)

    delexicalize = False
    delexicalize_after_grouping = False

    preprocess_data_multi_ref("devset.csv", "dev_multi_ref", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase, randomize_input_order, record_delimiter)

    preprocess_data_multi_ref("testset_w_refs.csv", "test", output_folder, delexicalize, delexicalize_after_grouping,
                              tokenize, lowercase, randomize_input_order, record_delimiter)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["word", "character", "template"])

    args = parser.parse_args()

    if args.mode == "character":
        prepare_character_based_experiment()

    elif args.mode == "word":
        prepare_word_based_delex_experiment()

    elif args.mode == "template":
        prepare_template_word_delex_experiment()
