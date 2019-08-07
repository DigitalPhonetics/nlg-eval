import unicodecsv as csv

import dataset
from record import Record


class E2EDataset(dataset.Dataset):
    def __init__(self, has_source=True, has_targets=True):
        super(E2EDataset, self).__init__(has_source, has_targets)
        self.has_targets = True

    def read_from_file(self, input_file):
        with open(input_file, "r") as f:
            csvread = csv.reader(f, encoding='UTF-8')
            csvread.next()  # skip header

            for line in csvread:

                records, target = line

                # process record
                records = records.split(", ")
                record_objs = []
                for record in records:
                    # records are of the form name[Alimentum]
                    record_components = record.split("[")
                    entity = record_components[0]
                    value = record_components[1][:-1]
                    record_obj = Record("", entity, value)
                    record_objs.append(record_obj)

                inputs = self.input_cls(record_objs)

                # process target
                targets_obj = self.target_cls(target)

                self.add_instance(inputs, targets_obj)
