import datetime
import re

import dataset
import input
import targets
from record import Record


class WebNLGDataset(dataset.Dataset):
    def __init__(self, has_source=True, has_targets=True):
        super(WebNLGDataset, self).__init__(has_source, has_targets)
        self.target_cls = WebNLGTargets

    def read_from_file(self, input_file):
        if self.has_source:
            self.read_dataset(input_file)
        else:
            self.read_dataset_only_targets(input_file)

    def read_dataset(self, file):
        with open(file) as f:
            for line in f.readlines():
                line = line.decode("utf-8")
                line = line.strip()
                line = line.replace("_", " ")

                if self.has_targets:
                    category, records, target = line.split("\t")
                else:
                    category, records = line.split("\t")
                    target = ""

                # process records
                records = records.replace("\"", "")
                records = records.split("<NEW-TRIPLE>")
                record_objs = []
                for record in records:
                    entity, type, value = record.split(" | ")
                    type_split_at_camel_case = " ".join(re.sub('(?!^)([A-Z][a-z]+)', r' \1', type).split())
                    record_obj = Record(type_split_at_camel_case, entity, value)
                    record_objs.append(record_obj)

                inputs = input.Input(record_objs)

                # process target
                targets_obj = self.target_cls(target)

                self.add_instance(inputs, targets_obj)

    def read_dataset_only_targets(self, file):
        target_objs = []
        with open(file) as f:
            for line in f.readlines():
                line = line.decode("utf-8")
                line = line.replace("_", " ")
                line = line.strip()
                if line == "":
                    self.add_instance(input.Input(), self.target_cls(target_objs))
                    target_objs = []
                else:
                    target_objs.append(line)


class WebNLGTargets(targets.Targets):
    @staticmethod
    def is_date(string):
        try:
            datetime.datetime.strptime(string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def ord(n):
        # else covers 11th-13th
        return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

    @staticmethod
    def get_month(int):
        months = "january february march april may june july august september october november december".split()
        int = int - 1
        if 0 <= int <= 11:
            return months[int]
        else:
            return ""

    @staticmethod
    def convert_to_text_date(date):
        # print "date", date
        month = WebNLGTargets.get_month(date.month)
        year = date.year
        day = WebNLGTargets.ord(date.day)
        date_string = "%s %s , %d" % (month, day, year)

        return date_string

    @staticmethod
    def normalize_date(string):
        """
        map date to format november 18th , 1923
        :param string:
        :return:
        """
        if WebNLGTargets.is_date(string):
            date = datetime.datetime.strptime(string, '%Y-%m-%d')
            string = WebNLGTargets.convert_to_text_date(date)
        return string

    def match_string_to_delexicalize(self, string_to_delex):
        # normalize date if necessary
        string_to_delex_with_normalized_date = WebNLGTargets.normalize_date(string_to_delex)
        return super(WebNLGTargets, self).match_string_to_delexicalize(string_to_delex_with_normalized_date)
