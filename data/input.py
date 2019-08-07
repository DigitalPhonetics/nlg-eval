from collections import OrderedDict
import numpy as np
import random

class Input(object):
    RELEX_ENTRIES_SEPARATOR = "<SEP>"
    RELEX_ENTRIES_FIELD_SEPARATOR = "<FIELD>"

    def __init__(self, records=None, sort_records=False):
        if not records:
            self.records = []
        else:
            self.records = records
        self.sort_records = sort_records
        self._sort_records()

        self.delex_dict = {} # lex_src -> delex
        self.relex_dict = {} # delex -> (lex_src, lex_tgt)
        self.tokenized = False

    @property
    def num_records(self):
        return len(self.records)

    @property
    def num_tokens(self):
        num_tokens = 0
        for record in self.records:
            record.tokenize()
            num_tokens += record.num_tokens
        return num_tokens

    def _sort_records(self):
        if self.sort_records:
            self.records = sorted(self.records, key= lambda r: (r.type, r.entity, r.value))

    def add_record(self, record):
        self.records.append(record)
        self._sort_records()

    def get_types(self):
        return [r.type for r in self.records]

    def get_entitites(self):
        return [r.entity for r in self.records]

    def get_values(self):
        return [r.value for r in self.records]

    def get_entities_and_values(self):
        values = {}
        for record in self.records:
            if record.entity in values:
                values[record.entity].add(record.value)
            else:
                values[record.entity] = set([record.value])

        return values

    def get_delex_candidates(self):
        """
        get candidates in decreasing order according to their length
        :return:
        """
        return sorted(self.delex_dict.keys(), key=len, reverse=True)

    def _add_delex_dict_entry(self, delex_prefix, concrete_names):
        for i, concrete_name in enumerate(concrete_names):
            self.delex_dict[concrete_name] = "%s-%d" %(delex_prefix, i)
            #self.relex_dict[delex_prefix + str(i)] = concrete_name

    def make_delex_dict_agent_patient_bridge(self):
        """
        delexicalization of entities and values
        strings that only appear as entities in the input are agents,
                                    values              are patients,
                    appear on both sides are bridges
        strategy adopted from http://webnlg.loria.fr/pages/tilburg_report.pdf
        :return:
        """
        entities = self.get_entitites()
        values = self.get_values()
        # entities.interesection(values)
        bridges = filter(lambda e: e in values and e in entities, entities+values)
        # remove duplicates
        bridges = list(OrderedDict.fromkeys(bridges))
        # entities.difference(values)
        agents = filter(lambda e: e not in values, entities)
        agents = list(OrderedDict.fromkeys(agents))
        # values.difference(entities)
        patients = filter(lambda v: v not in entities, values)
        patients = list(OrderedDict.fromkeys(patients))

        self._add_delex_dict_entry("BRIDGE", bridges)
        self._add_delex_dict_entry("AGENT", agents)
        self._add_delex_dict_entry("PATIENT", patients)

        for record in self.records:
            for concrete, delex in self.delex_dict.items():
                record.maybe_set_delexicalized_entity_or_value(concrete, delex)

    def make_delex_dict_entities(self, entities_to_delexicalize):
        """
        delexicalize values of the given entities as ENTITY-X
        :return:
        """
        for record in self.records:
            if record.entity in entities_to_delexicalize and record.value:
                record.set_delexicalized_value()
                #delex_value = record.entity.upper() + "-X"
                self.delex_dict[record.value] = record.delexicalized_value


    def make_delex_dict(self, entities=None, agent_patient_bridge=False):
        if agent_patient_bridge:
            self.make_delex_dict_agent_patient_bridge()
        elif entities is not None:
            self.make_delex_dict_entities(entities)

    def as_string(self, delimiter=None, flat_record =False, randomize_record_order=False):
        if delimiter is None:
            if self.tokenized:
                delimiter = " , "
            else:
                delimiter = ","
        records = self.records
        # print "randomize record order is", randomize_record_order
        if randomize_record_order:
            random.shuffle(records)
        return delimiter.join(map(lambda r: r.as_string(flat_record), records))

    def get_records_as_string(self):
        return [r.as_string() for r in self.records]

    def tokenize(self):
        self.tokenized = True

    def lowercase(self):
        for record in self.records:
            record.lowercase()

    def delexicalize(self, delexicalized_string):
        for record in self.records:
            record.delexicalize(delexicalized_string)

        self._sort_records()

    def lexicalize(self):
        for record in self.records:
            record.lexicalize(self.relex_dict)

    def relexicalization_line_as_string(self):
        relex_tuple_strings = []
        for delex_string in self.relex_dict:
            lex = self.relex_dict[delex_string]
            # different lexicalizations for same delex entity in src and tgt
            # e.g. for (WebNLG dates)
            if len(lex) == 2:
                lex_src, lex_tgt = lex
            else: # same lexicalization - copy lex string
                lex_src, lex_tgt = lex, lex
            relex_tuple_string = "%s%s%s%s%s" % (
            delex_string, Input.RELEX_ENTRIES_FIELD_SEPARATOR, lex_src, Input.RELEX_ENTRIES_FIELD_SEPARATOR, lex_tgt)
            relex_tuple_strings.append(relex_tuple_string.encode("utf-8"))
        return Input.RELEX_ENTRIES_SEPARATOR.join(relex_tuple_strings)

    def make_vector(self, unique_record_list):
        arr = []
        # print "template has %d entries" %len(template)
        # print "template", template
        own_records = self.get_records_as_string()
        for i, slot_value_pair in enumerate(unique_record_list):
            if slot_value_pair in own_records:
                arr.append(1)
            else:
                arr.append(0)

        self.vector = np.array(arr)