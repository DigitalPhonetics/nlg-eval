import argparse

import dataset_e2e
import dataset_rnnlg
import dataset_webnlg
import dataset_bagel
import options
from dataset import Dataset


def print_args(args):
    print "dataset_path\t%s" % (str(args.dataset_path))
    print "dataset_type\t%s" % (str(args.dataset_type))
    print "output_path\t%s" % (str(args.output_path))
    print "only_source\t%s" % (str(args.only_source))
    print "multi_reference\t%s" % (str(args.multi_reference))
    print "lowercase\t%s" % (str(args.lowercase))
    print "tokenize\t%s" % (str(args.tokenize))
    print "tokenize_src\t%s" % (str(args.tokenize_src))
    print "tokenize_tgt\t%s" % (str(args.tokenize_tgt))
    print "delexicalize\t%s" % (str(args.delexicalize))
    print "delexicalize after grouping\t%s" % (str(args.delexicalize_after_grouping))
    print "group_inputs\t%s" % (str(args.group_inputs))
    print "collect multi references\t%s" % (str(args.collect_multi_references))
    print "entities to delexicalize\t%s" % (" ".join(args.entities_to_delexicalize))


def read_dataset(args):
    # delexicalization type
    agent_patient_bridge = False
    force_delex_source = True

    dataset = None
    if args.dataset_type == "webnlg":
        has_targets = not (args.only_source)
        has_source = not (args.multi_reference)
        dataset = dataset_webnlg.WebNLGDataset(has_source=has_source, has_targets=has_targets)
        dataset.read_from_file(args.dataset_path)
        agent_patient_bridge = True

    elif args.dataset_type == "e2e":
        dataset = dataset_e2e.E2EDataset()
        dataset.read_from_file(args.dataset_path)

    elif args.dataset_type == "rnnlg":
        dataset = dataset_rnnlg.RNNLGDataset()
        dataset.read_from_file(args.dataset_path, args.multi_reference)

    elif args.dataset_type == "bagel":
        dataset = dataset_bagel.BAGELDataset()
        dataset.read_from_file(args.dataset_path)

    elif "preprocessed" in args.dataset_type:
        dataset = Dataset()
        dataset.read_from_file(args.dataset_path)
        if "webnlg" in args.dataset_type:
            agent_patient_bridge = True

    return dataset, force_delex_source, agent_patient_bridge


def process_dataset(args):
    print "processing dataset"
    print_args(args)

    # TODO later on change implementation of delex such that each dataset has own delex method
    # and agent_patient_bridge is not needed anymore
    dataset, force_delex_source, agent_patient_bridge = read_dataset(args)


    dataset.maybe_tokenize(args.tokenize_src, args.tokenize_tgt)

    if args.lowercase:
        dataset.lowercase()

    dataset.print_info()

    if args.delexicalize and not args.delexicalize_after_grouping:
        dataset.delexicalize(args.entities_to_delexicalize, agent_patient_bridge, force_delex_source)
        if not args.separate_inputs_for_number_of_records:
            dataset.write_relexicalization_file(args.relexicalization_file)

        print "updated statistics after delexicalization"
        dataset.print_info()

    if args.group_inputs:
        dataset.group_inputs()

        print "updated statistics after grouping"
        dataset.print_info()

    if args.delexicalize_after_grouping:
        dataset.delexicalize(args.entities_to_delexicalize, agent_patient_bridge, force_delex_source)
        if not args.separate_inputs_for_number_of_records:
            dataset.write_relexicalization_file(args.relexicalization_file)

        print "updated statistics after delexicalization after grouping"
        dataset.print_info()

    if args.collect_multi_references:
        print "collect multi references"
        dataset.collect_multi_references(args.entities_to_delexicalize, agent_patient_bridge)

    multi_reference = args.multi_reference or args.group_inputs or args.collect_multi_references

    print "args.randomize_record_order" is args.randomize_record_order
    if multi_reference:
        if args.separate_inputs_for_number_of_records:
            dataset.write_multi_reference_separate_for_number_of_records_with_relex_files \
                (args.output_path, args.output_path_references, args.relexicalization_file, args.record_delimiter,
                 args.flatten_records, args.randomize_record_order)
        else:
            dataset.write_multi_reference(args.output_path, args.output_path_references,
                                          args.record_delimiter, args.flatten_records, args.randomize_record_order)
    else:
        outfile_references = None
        if args.output_path_references:
            outfile_references = args.output_path_references
        if args.separate_inputs_for_number_of_records:
            dataset.write_single_reference_separate_for_number_of_records(args.output_path, outfile_references,
                                                                          record_delimiter=args.record_delimiter,
                                                                          flatten_records=args.flatten_records,
                                                                          randomize_record_order=args.randomize_record_order)
        else:
            dataset.write_single_reference(args.output_path, outfile_references,
                                           record_delimiter=args.record_delimiter, flatten_records=args.flatten_records,
                                           randomize_record_order=args.randomize_record_order)

    return dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = options.dataset_options(parser)

    args = parser.parse_args()

    process_dataset(args)
