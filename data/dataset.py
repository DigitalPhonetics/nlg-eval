import delexicalize
import statistics
import json
from input import Input
from targets import Targets
from record import Record
import collections
import copy
import numpy as np
import re
import operator


class Dataset(object):
    def __init__(self, has_source=True, has_targets=True):
        self.inputs = []
        self.targets = []
        self.has_source = has_source
        self.has_targets = has_targets
        self.tokenized_src = False
        self.tokenized_tgt = False
        self.delexicalized = False
        self.target_cls = Targets
        self.input_cls = Input
        # list of unique records to create input vectors
        self.unique_records = []

    def read_from_file(self, input_file):
        # TODO for preprocessed data, will not work if inputs contain " , " except for delimiting records
        # for now only works for tokenized data
        # only works with source + target or only source but not with only target
        self.tokenized_src = True
        self.tokenized_tgt = True
        record_with_type = re.compile(r"(.*) \( (.*) \[ (.*) \] \)$")
        record_without_type = re.compile(r"(.*) \[ (.*) \]$")
        with open(input_file) as f:
            for line in f.readlines():
                # print line
                line = line.decode("utf-8")
                line = line.strip()

                # can read source + target or only source
                line = line.split("\t")
                if len(line) == 2:
                    records, target = line
                else:
                    records = line[0]
                    target = ""
                # process records
                records = records.split(" , ")
                record_objs = []
                for record in records:
                    matched_record_with_type = record_with_type.match(record)
                    if matched_record_with_type:
                        type = matched_record_with_type.group(1)
                        entity = matched_record_with_type.group(2)
                        value = matched_record_with_type.group(3)
                    else:
                        matched_record_without_type = record_without_type.match(record)
                        if matched_record_without_type:
                            type = ""
                            entity = matched_record_without_type.group(1)
                            value = matched_record_without_type.group(2)
                        else:
                            print "invalid record", record

                    record_obj = Record(type, entity, value)
                    record_obj.tokenized = True
                    record_objs.append(record_obj)

                inputs = Input(record_objs)
                inputs.tokenized = True

                # process target
                targets_obj = self.target_cls(target)
                targets_obj.tokenized = True

                self.add_instance(inputs, targets_obj)

    def add_instance(self, input, targets):
        self.inputs.append(input)
        self.targets.append(targets)

    def get_average_number_of_targets(self):
        if len(self.targets) == 0:
            return 0.0
        else:
            total_number_of_references = [t.number_of_references for t in self.targets]

            return sum(total_number_of_references) / float(len(self.targets))

    def get_input_statistics(self):
        record_statistics = statistics.Statistics("number of records per input")
        for input in self.inputs:
            record_statistics.update(len(input.records))
        return record_statistics.as_string()

    def get_input_statistics_tokenized(self):
        input_statistics_tokens = statistics.Statistics("number of tokens per input")

        for input in self.inputs:
            input_statistics_tokens.update(input.num_tokens)

        return input_statistics_tokens.as_string()

    def get_input_statistics_string_formatted(self):
        entity_type = "characters"
        if self.tokenized_src:
            entity_type = "tokens"
        input_statistics_length = statistics.Statistics("number of %s in formatted input" % entity_type)
        for input in self.inputs:
            input_as_string = input.as_string()
            if self.tokenized_src:
                split_input = input_as_string.split()
            else:
                split_input = list(input_as_string)
            input_statistics_length.update(len(split_input))

        return input_statistics_length.as_string()

    def get_target_statistics(self):
        target_statistics = statistics.Statistics("number of references")
        for target in self.targets:
            target_statistics.update(target.number_of_references)
        return target_statistics.as_string()

    def get_target_statistics_tokenized(self):
        target_statistics_sentences = statistics.Statistics("number of sentences per reference")
        target_statistics_tokens = statistics.Statistics("number of tokens per reference")

        for target in self.targets:
            target_statistics_sentences.update_from_statistics_object(target.sentence_stats)
            target_statistics_tokens.update_from_statistics_object(target.token_stats)

        return target_statistics_sentences.as_string(), target_statistics_tokens.as_string()

    def get_target_statistics_num_characters(self):
        target_statistics_characters = statistics.Statistics("number of characters in targets")
        for target in self.targets:
            for target_string in target.targets:
                if self.tokenized_tgt:
                    split_target = target_string.split()
                else:
                    split_target = list(target_string)

                target_statistics_characters.update(len(split_target))

        return target_statistics_characters.as_string()

    def get_target_statistics_tokenized_delexicalized(self):
        target_statistics_tokens_delexicalized = statistics.Statistics("number of tokens per delexicalized reference")
        if self.delexicalized:
            for targets_for_instance in self.targets:
                # print "targets: %d " %target.delex_token_stats.instances
                for target in targets_for_instance.targets:
                    target_statistics_tokens_delexicalized.update(len(target.split()))
                # target_statistics_tokens_delexicalized.update_from_statistics_object(target.delex_token_stats)
        return target_statistics_tokens_delexicalized.as_string()

    def get_types(self):
        types = set([])
        for input in self.inputs:
            types.update(input.get_types())
        return types

    def get_entities(self):
        entities = set([])
        for input in self.inputs:
            entities.update(input.get_entitites())
        return entities

    def get_entities_and_values(self):
        values = {}
        for input in self.inputs:
            current_values = input.get_entities_and_values()
            for entity in current_values:
                if entity in values:
                    values[entity].update(current_values[entity])
                else:
                    values[entity] = current_values[entity]
        return values

    def make_unique_records_list(self):
        unique_records = set([])
        for input in self.inputs:
            for record_string in input.get_records_as_string():
                unique_records.add(record_string)
        self.unique_records = list(unique_records)

    def make_input_vectors(self):
        if len(self.unique_records) == 0:
            raise AttributeError("Trying to make input vectors without having unique_records."
                                 "First call set_unique_records or make_unique_records_list.")
        for input in self.inputs:
            input.make_vector(self.unique_records)

        input_vectors = [i.vector for i in self.inputs]
        self.input_vectors = np.array(input_vectors)

    def set_unique_records(self, unique_records):
        self.unique_records = unique_records

    def hamming_distance(self, input_arr, arrays_to_compare):
        """
        compute hamming distance of input_arr to each of the arrays in
        arrays_to_compare
        :param input_arr:
        :param arrays_to_compare:
        :return:
        """
        # xor
        xor = np.logical_xor(input_arr, arrays_to_compare)
        # print "xor", xor.shape, xor
        distance = np.sum(xor, axis=1)
        # print "distance", distance.shape, distance
        return distance

    def most_similar(self, input, topn=10):
        if self.unique_records is None:
            raise AttributeError("Trying to make input vectors without having unique_records."
                                 "First call set_unique_records or make_unique_records_list.")

        # print "records vector has the following entries", self.unique_records
        # print "array of vectors for all inputs", self.input_vectors
        # print "input", input.as_string()

        input.make_vector(self.unique_records)
        # print "the vector for the input is ", input.vector

        # compute distance
        distances = self.hamming_distance(input.vector, self.input_vectors)
        most_similar_inputs = np.argsort(distances, axis=0)[:topn]
        smallest_distances = np.take(distances, most_similar_inputs)
        # print most_similar_inputs
        return most_similar_inputs, smallest_distances

    def print_info(self):
        print "number of instances\t%d" % len(self.inputs)
        # print "avg number of references:\t%.2f" %(self.get_average_number_of_targets())
        print self.get_input_statistics()

        if self.tokenized_src:
            print self.get_input_statistics_tokenized()

        print self.get_input_statistics_string_formatted()

        if self.has_targets:
            print self.get_target_statistics()

            if self.tokenized_tgt:
                target_statistics_sentences, target_statistics_tokens = self.get_target_statistics_tokenized()
                print target_statistics_sentences
                print target_statistics_tokens
            else:
                print self.get_target_statistics_num_characters()

            if self.delexicalized:
                print self.get_target_statistics_tokenized_delexicalized()

        types = self.get_types()
        print "%d types: %s" % (len(types), ", ".join(sorted(types)).encode("utf-8"))
        entities = self.get_entities()
        print "%d entities: %s" % (len(entities), ", ".join(sorted(entities)).encode("utf-8"))
        values = self.get_entities_and_values()
        for entity in sorted(values):
            print "%s: %s" % (entity.encode("utf-8"), ", ".join(sorted(values[entity])).encode("utf-8"))

    def write_single_reference_for_inputs_and_targets(self, inputs, targets, outfile, outfile_tgt, record_delimiter,
                                                      flatten_records, randomize_record_order):
        # write to separate src and tgt files
        if outfile_tgt:
            with open(outfile, "w") as out_inputs, open(outfile_tgt, "w") as out_targets:
                for i, input in enumerate(inputs):
                    for target in targets[i].targets:
                        # out_inputs.write(("%s\t%s\n" %(input.as_string(tokenized), self.targets[i].as_string())).strip() + "\n\n")
                        out_inputs.write("%s\n" % (input.as_string(record_delimiter, flatten_records,
                                                                   randomize_record_order=randomize_record_order)).strip())
                        out_targets.write("%s\n" % (target.encode("utf-8")))
        # write to one file, src + tgt separated by tab
        else:
            with open(outfile, "w") as outf:
                for i, input in enumerate(inputs):
                    for target in targets[i].targets:
                        outf.write(("%s\t%s" % (input.as_string(record_delimiter, flatten_records,
                                                                randomize_record_order=randomize_record_order),
                                                target.encode("utf-8"))).strip() + "\n")

    def write_single_reference(self, outfile, outfile_tgt=None, record_delimiter=None, flatten_records=False,
                               randomize_record_order=False):
        self.write_single_reference_for_inputs_and_targets(self.inputs, self.targets, outfile, outfile_tgt,
                                                           record_delimiter, flatten_records, randomize_record_order)

    def write_single_reference_separate_for_number_of_records(self, outfile, outfile_tgt=None, record_delimiter=None,
                                                              flatten_records=False, randomize_record_order=False):
        input_ids_grouped_for_number_of_records = self.group_inputs_for_number_of_records()
        outfile_tgt_for_record_n = None
        for number_of_records in input_ids_grouped_for_number_of_records:
            outfile_inputs_for_record_n = outfile.replace(".txt", "_%d.txt" % number_of_records)
            if outfile_tgt:
                outfile_tgt_for_record_n = outfile_tgt.replace(".txt", "_%d.txt" % number_of_records)
            get_items = operator.itemgetter(*input_ids_grouped_for_number_of_records[number_of_records])
            inputs = get_items(self.inputs)
            targets = get_items(self.targets)
            self.write_single_reference_for_inputs_and_targets(inputs, targets, outfile_inputs_for_record_n,
                                                               outfile_tgt_for_record_n, record_delimiter,
                                                               flatten_records, randomize_record_order)

    def write_multi_reference_separate_for_number_of_records_with_relex_files \
                    (self, outfile_inputs, outfile_targets, outfile_relex,
                     record_delimiter=None,
                     flatten_records=False, randomize_record_order=False):
        input_ids_grouped_for_number_of_records = self.group_inputs_for_number_of_records()

        for number_of_records in input_ids_grouped_for_number_of_records:
            outfile_inputs_for_number_of_records = outfile_inputs.replace(".txt", "_%d.txt" % number_of_records)
            outfile_targets_for_number_of_records = outfile_targets.replace(".txt", "_%d.txt" % number_of_records)
            get_items = operator.itemgetter(*input_ids_grouped_for_number_of_records[number_of_records])
            inputs = get_items(self.inputs)
            targets = get_items(self.targets)
            self.write_multi_reference_for_input_and_targets(inputs, targets, outfile_inputs_for_number_of_records,
                                                             outfile_targets_for_number_of_records,
                                                             record_delimiter, flatten_records, randomize_record_order)

            outfile_relex_for_number_of_records = outfile_relex.replace(".txt", "_%d.txt" % number_of_records)
            Dataset.write_relexicalization_file_for_inputs(inputs, outfile_relex_for_number_of_records)

    def group_inputs_for_number_of_records(self):
        input_ids_grouped_for_number_of_records = collections.defaultdict(list)

        for i, input in enumerate(self.inputs):
            input_ids_grouped_for_number_of_records[input.num_records].append(i)
        return input_ids_grouped_for_number_of_records

    def write_multi_reference_for_input_and_targets(self, inputs, targets, outfile_inputs, outfile_targets,
                                                    record_delimiter, flatten_records, randomize_record_order):
        with open(outfile_inputs, "w") as out_inputs, open(outfile_targets, "w") as out_targets:
            for input, target in zip(inputs, targets):
                out_inputs.write("%s\n" % (input.as_string(record_delimiter, flatten_records,
                                                           randomize_record_order=randomize_record_order)).strip())
                out_targets.write("%s\n\n" % (target.as_string()))

    def write_multi_reference(self, outfile_inputs, outfile_targets, record_delimiter=None, flatten_records=False,
                              randomize_record_order=False):
        self.write_multi_reference_for_input_and_targets(self.inputs, self.targets, outfile_inputs, outfile_targets,
                                                         record_delimiter, flatten_records, randomize_record_order)

    def maybe_tokenize(self, tokenize_src, tokenize_tgt):
        if tokenize_src:
            for input in self.inputs:
                input.tokenize()
                self.tokenized_src = True
        if tokenize_tgt:
            for target in self.targets:
                target.tokenize()
                self.tokenized_tgt = True

    def lowercase(self):
        for input in self.inputs:
            input.lowercase()
        for target in self.targets:
            target.lowercase()

    def delexicalize(self, entities_to_delexicalize, agent_patient_bridge, force_delex_source):
        for input in self.inputs:
            input.make_delex_dict(entities_to_delexicalize, agent_patient_bridge)

        if agent_patient_bridge:
            only_delex_value = False
        else:
            only_delex_value = True

        # delex_inputs = []
        # delex_targets = []
        print "delexicalize dataset"
        for input, targets in zip(self.inputs, self.targets):
            delexicalize.delexicalize_instance(input, targets, only_delex_value, self.has_targets, force_delex_source)

            # delex_inputs.append(delex_input)
            # delex_targets.append(delex_targets_obj)

        # self.inputs = delex_inputs
        # self.targets = delex_targets

        self.delexicalized = True

    def collect_multi_references(self, entities_to_delexicalize, agent_patient_bridge):
        for input in self.inputs:
            input.make_delex_dict(entities_to_delexicalize, agent_patient_bridge)

        if agent_patient_bridge:
            only_delex_value = False
        else:
            only_delex_value = True

        for i, (input, targets_obj) in enumerate(zip(self.inputs, self.targets)):
            delexicalize.delexicalize_instance(input, targets_obj, only_delex_value, self.has_targets,
                                               force_delex_source=False)

        grouped_inputs = Dataset.group_inputs_in_dict(self.inputs, self.targets)

        # relexicalize the targets
        extended_targets = []
        for j, input in enumerate(self.inputs):
            _, delexicalized_grouped_targets = grouped_inputs[input.as_string()]

            input.lexicalize()
            # important, otherwise the entries in the dictionary are changed
            lexicalized_grouped_targets = copy.deepcopy(delexicalized_grouped_targets)
            lexicalized_grouped_targets.lexicalize(input.relex_dict)

            extended_targets.append(lexicalized_grouped_targets)

        self.targets = extended_targets

    @staticmethod
    def write_relexicalization_file_for_inputs(inputs, output_file):
        with open(output_file, "w") as of:
            for input in inputs:
                of.write(input.relexicalization_line_as_string() + "\n")

    def write_relexicalization_file(self, output_file):
        Dataset.write_relexicalization_file_for_inputs(self.inputs, output_file)

    @staticmethod
    def group_inputs_in_dict(inputs, targets):
        """
        group all instances with same inputs
        in one instance with multiple targets
        assumes that records in input are already ordered:
         inputs area[north], family_friendly[no] and family_friendly[no], area[north] will not be merged
        :return:
        """
        unique_inputs = collections.OrderedDict()  # dict of input_strings -> (inputs obj, targets obj)

        for input, target_obj in zip(inputs, targets):
            input_string = input.as_string()
            if input_string in unique_inputs:
                unique_input, unique_targets = unique_inputs[input_string]
                unique_targets.add_targets(target_obj)
            else:
                unique_inputs[input_string] = (input, target_obj)

        return unique_inputs

    def group_inputs(self):
        grouped_inputs = Dataset.group_inputs_in_dict(self.inputs, self.targets)

        self.inputs, self.targets = zip(*grouped_inputs.values())
