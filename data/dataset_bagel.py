# reads in original BAGEL file
# and prints it, grouped according to abstracted/delexicalized DAs
# in the following format:
# abstract_DA
# full_DA 1
# full_DA 2
# reference abstracted 1
# reference abstracted 2
import re
import collections
import random
import os
import logging

import dataset
from record import Record
import input
import targets
from tokenizer import sent_tokenize_return_string_and_length

class BAGELDataset():
    def __init__(self, delexicalize, lowercase, tokenize):
        self.instances = collections.defaultdict(list)
        self.delexicalize = delexicalize
        self.lowercase = lowercase
        self.tokenize = tokenize
        self.input_cls = input.Input
        logging.basicConfig(level=logging.INFO)

    DA_REGEX = re.compile(r".+_(DA|da) = inform\((.+)\)$")
    DELEX_VALUE_REGEX = re.compile(r"[Xx][1-9]$")
    TEXT_REGEX = re.compile(r"-> \"(.+)\";$")
    DELEX_WORD_REGEX = re.compile(r"\[(.+)\+[Xx]\][Xx]")

    def _process_da(self, da_line):
        slot_value_pairs = BAGELDataset.DA_REGEX.match(da_line).group(2)
        # replace ", " to avoid splitting names in values, later substitute again
        slot_value_pairs = slot_value_pairs.replace(", ", "PUNCTUATION_COMMA")
        slot_value_pairs = slot_value_pairs.split(",")
        processed_slot_value_pairs = []
        logging.debug("slot value pairs: %s" %slot_value_pairs)
        for slot_value_pair in slot_value_pairs:
            slot_value_pair = slot_value_pair.replace("PUNCTUATION_COMMA", ", ")
            slot, value = slot_value_pair.split("=")
            value = value.strip("\"")
            processed_slot_value_pairs.append((slot, value))
        return processed_slot_value_pairs

    def _process_abstracted_da(self, da_line):
        """
        map BAGEL abstraction format to my format
        (area=X2 -> area=AREA-X-2)
        :param da_line:
        :return:
        """
        entity_value_pairs = self._process_da(da_line)
        delex_dict = collections.defaultdict(list)
        processed_entity_value_pairs = []
        for entity, value in entity_value_pairs:
            if BAGELDataset.DELEX_VALUE_REGEX.match(value):
                value = entity.upper()
                if entity in delex_dict:
                    entity_counter = len(delex_dict[entity])
                    entity_counter += 1
                else:
                    entity_counter = 1
                value = "%s-X-%d" % (value, entity_counter)
                delex_dict[entity].append(value)
            processed_entity_value_pairs.append((entity, value))
        return processed_entity_value_pairs, delex_dict

    def _map_entity_value_pairs_to_input(self, entity_value_pairs):
        records = [Record("", entity, value) for (entity, value) in entity_value_pairs]
        # sort_records=True yields 143 uniq instances, sort_records=False 202
        input = self.input_cls(records, sort_records=False)
        #if self.tokenize:
        #    input.tokenize()
        return input

    def _get_own_delex_word(self, entity, num_entity_already_delex, delex_entity_dict):
        """
        :param entity:
        :param num_entity_already_delex: how many times we have already seen values of this entity in the text
        :param delex_entity_dict: maps entities to list of their delexicalized values
        :return:
        """
        delex_values = delex_entity_dict[entity]
        # catch case that one value of an entity is mentioned multiple times in the text
        # always return it's last value
        if num_entity_already_delex >= (len(delex_values) -1):
            # print "multiple mentions of same entity", entity
            return delex_values[-1]
        else:
            return delex_values[num_entity_already_delex]

    def _process_text(self, text_line, delex_entity_dict, delex_dict, relex_dict):
        text = BAGELDataset.TEXT_REGEX.match(text_line).group(1)
        delexicalized_entities_counter = collections.defaultdict(int)
        # print "delex_entities_dict: %s, delex_dict: %s, relex_dict: %s" %(str(delex_entity_dict), str(delex_dict), str(relex_dict))
        words = []
        delexicalized_words = []
        for word in text.split():
            delex_word = BAGELDataset.DELEX_WORD_REGEX.match(word)
            if delex_word:
                entity = delex_word.group(1)
                num_entity_already_delex = delexicalized_entities_counter[entity]
                # print "entity: %s, num_entity_already_delex: %d" \
                #     %(entity, num_entity_already_delex)

                own_delex_word = self._get_own_delex_word(entity, num_entity_already_delex, delex_entity_dict)
                #own_delex_word = delex_entity_dict[entity][num_entity_already_delex]
                # lexicalize the text
                word = relex_dict[own_delex_word]
                delexicalized_entities_counter[entity] += 1
            else:
                # remove the brackets
                word = re.sub(r'\[.*\]', "", word)
                own_delex_word = word

            words.append(word)
            delexicalized_words.append(own_delex_word)

        #tokenize the text
        text = " ".join(words)
        delexicalized_text = " ".join(delexicalized_words)
        #if self.tokenize:
        #    text, num_sents, num_tokens = sent_tokenize_return_string_and_length(text)
        #    delexicalized_text, num_sents, num_tokens = sent_tokenize_return_string_and_length(delexicalized_text)

        #print "delexicalized text: ", delexicalized_text
        #print "concrete text:", text
        return delexicalized_text, text

    def _group_entities(self, entity_value_pairs):
        entities = collections.defaultdict(list)
        for entity, value in entity_value_pairs:
            entities[entity].append(value)
        return entities

    def _make_relex_dict(self, entity_value_pairs, delex_entity_dict):
        relex_dict = {}
        delex_dict = {}
        grouped_entities = self._group_entities(entity_value_pairs)
        for entity in delex_entity_dict:
            for i, delex_val in enumerate(delex_entity_dict[entity]):
                own_delex_val = grouped_entities[entity][i]
                relex_dict[delex_val] = own_delex_val
                #print "grouped entity", own_delex_val
                delex_dict[own_delex_val] = delex_val

        return delex_dict, relex_dict

    def read_from_file(self, input_file):
        with open(input_file, "r") as f:
            input_obj = None
            lexicalized_input_obj = None
            delex_dict = None
            relex_dict = None
            for line_counter, line in enumerate(f.readlines()):
                line = line.strip()
                if self.lowercase:
                    line = line.lower()

                # process lexicalized DA
                if line.lower().startswith("full_da"):
                    lexicalized_entity_value_pairs = self._process_da(line)
                    lexicalized_input_obj = self._map_entity_value_pairs_to_input(lexicalized_entity_value_pairs)
                    #self.lexicalized_inputs.append()

                elif line.lower().startswith("abstract_da"):
                    delexicalized_entity_value_pairs, delex_entity_dict = self._process_abstracted_da(line)
                    delex_dict, relex_dict = self._make_relex_dict(lexicalized_entity_value_pairs, delex_entity_dict)
                    input_obj = self._map_entity_value_pairs_to_input(delexicalized_entity_value_pairs)
                    input_obj.relex_dict = relex_dict
                # process targets and append instance
                elif line.startswith("->"):
                    target, lexicalized_target = self._process_text(line, delex_entity_dict, delex_dict, relex_dict)
                    #TODO input_obj is always the same for same key but other data fields are different
                    self.instances[input_obj.as_string()].append((input_obj, lexicalized_input_obj, target, lexicalized_target))

                    #self.add_instance(input_obj, targets_obj)

    def make_dataset(self, inputs, targets):
        dataset_ = dataset.Dataset()
        #dataset_.tokenized = self.tokenize
        dataset_.delexicalized = self.delexicalize
        for (input, target_obj) in zip(inputs, targets):
            dataset_.add_instance(input, target_obj)

        if self.tokenize:
            dataset_.tokenize()

        return dataset_

    def write_train_dev_data(self, output_dir, prefix, input_keys, char_based=False):
        instance_lists = [self.instances[input_key] for input_key in input_keys]
        # make the dataset
        if self.delexicalize:
            src_tuple_idx = 0
            tgt_tuple_idx = 2
        else:
            src_tuple_idx = 1
            tgt_tuple_idx = 3

        inputs = [instance[src_tuple_idx] for instance_list in instance_lists for instance in instance_list]
        target_objs = [targets.Targets(instance[tgt_tuple_idx]) for instance_list in instance_lists for instance in instance_list]
        dataset_ = self.make_dataset(inputs, target_objs)

        outfile_src = output_dir + "/%s_src.txt" %prefix
        outfile_tgt = output_dir + "/%s_tgt.txt" %prefix
        #print "inputs", dataset_.inputs[0]
        dataset_.print_info()
        dataset_.write_single_reference(outfile_src, outfile_tgt)

        if self.delexicalize:
            outfile_relex = output_dir + "/%s_relex.txt" % prefix
            dataset_.write_relexicalization_file(outfile_relex)


    def write_test_data(self, output_dir, input_keys, char_based=False):
        instance_lists = [self.instances[input_key] for input_key in input_keys]
        # make the dataset
        if self.delexicalize:
            src_tuple_idx = 0
            tgt_tuple_idx = 2
            # only select first delexicalized input object (have twice the same)
            inputs = [instance_list[0][src_tuple_idx] for instance_list in instance_lists]
            # make list of both targets
            #for instance_list in instance_lists:
            #    print instance_list[:]
            target_objs = []
            for instance_list in instance_lists:
                targets_ = []
                for instance in instance_list:
                    targets_.append(instance[tgt_tuple_idx])

                logging.debug("targets: %s" %str(targets_))
                target_objs.append(targets.Targets(targets_))

        else:
            src_tuple_idx = 1
            tgt_tuple_idx = 3
            inputs = [instance[src_tuple_idx] for instance_list in instance_lists for instance in instance_list]
            target_objs = [targets.Targets(instance[tgt_tuple_idx]) for instance_list in instance_lists for instance in instance_list]

        dataset_ = self.make_dataset(inputs, target_objs)

        outfile_src = output_dir + "/test_src.txt"
        outfile_tgt = output_dir + "/test_tgt.txt"
        dataset_.print_info()
        dataset_.write_multi_reference(outfile_src, outfile_tgt)

        if self.delexicalize:
            outfile_relex = output_dir + "/test_relex.txt"
            dataset_.write_relexicalization_file(outfile_relex)

    def write_cross_validation_files(self, output_dir, num_folds):
        num_dev_instances = 10

        input_keys = self.instances.keys()
        num_unique_instances = len(input_keys)
        print "%d unique instances" %num_unique_instances

        random.seed = 1234
        # randomize order
        # create ordering
        ordering = range(num_unique_instances)
        random.shuffle(ordering)

        #TODO copied this from tgen (https://github.com/UFAL-DSG/tgen/blob/master/bagel-data/input/cv_split.py)
        # check it
        # output as train and test into all CV portions
        fold_size, bigger_folds = divmod(num_unique_instances, num_folds)
        for fold_no in xrange(num_folds):
            # compute test data bounds
            if fold_no < bigger_folds:
                test_lo = (fold_size + 1) * fold_no
                test_hi = (fold_size + 1) * (fold_no + 1)
            else:
                test_lo = fold_size * fold_no + bigger_folds
                test_hi = fold_size * (fold_no + 1) + bigger_folds
            # select train and test data instances
            train_data = [input_keys[idx] for ord, idx in enumerate(ordering)
                          if ord < test_lo or ord >= test_hi]
            test_data = [input_keys[idx] for ord, idx in enumerate(ordering)
                         if ord >= test_lo and ord < test_hi]

            output_dir_fold = output_dir +  "%02d" %fold_no
            if not os.path.exists(output_dir_fold):
                os.makedirs(output_dir_fold)

            self.write_train_dev_data(output_dir_fold, "train", train_data[:-num_dev_instances])
            self.write_train_dev_data(output_dir_fold, "dev", train_data[-num_dev_instances:])
            self.write_test_data(output_dir_fold, test_data)
