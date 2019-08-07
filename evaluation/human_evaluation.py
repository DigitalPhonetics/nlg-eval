import random
import collections
import argparse
import os
import operator
import itertools

class NLGDataInstance():
    def __init__(self, n_global, n, random_order_n, num_inputs, model, src, tgt, annotations):
        self.id = None
        self.n_global = n_global
        self.n = n
        self.random_order_n = random_order_n
        self.num_inputs = num_inputs
        self.model = model
        self.src = src
        self.tgt = [tgt]
        self.annotations = annotations

    def set_id(self, id):
        self.id = str(id)

    def as_str_to_annotate(self):
        return ("%s\t%s\t%s\n" %(self.id, self.src, "\t".join(self.tgt))).encode("utf-8")

    def set_tgts(self, tgts):
        self.tgt = tgts

    def as_str_to_analyze(self):
        return ("%s\t%d\t%d\t%d\t%s\t%s\n" % (self.id, self.n_global, self.n, self.num_inputs, self.model, self.annotations)).encode("utf-8")

class NLGData():
    def __init__(self, dataset, src_file, tgt_file, modelname, randomly_ordered_instances_file=None):
        print "dataset %s" %dataset
        self.dataset = dataset
        if dataset == "e2e":
            # E2E instances for the different input lengths
            num_inputs = [3, 4, 5, 6, 7, 8]
            num_instances = [30, 37, 15, 194, 200, 71]
        elif dataset == "webnlg":
            num_inputs = [1, 2, 3, 4, 5, 6, 7]
            num_instances = [225, 152, 171, 162, 116, 23, 22]
        self.inputs_with_num_instances = zip(num_inputs, num_instances)
        self.modelname = modelname
        self.inputs = self.read_lines(src_file)
        self.targets = self.read_lines(tgt_file)
        self.n_for_inputs_with_length = self.get_n_for_inputs_with_length()
        print "number of inputs with length %s" % str([(length, len(n)) for length, n in self.n_for_inputs_with_length.items()])

        if os.path.isfile(randomly_ordered_instances_file) and os.path.getsize(randomly_ordered_instances_file) > 0:
            self.read_ranomly_ordered_instances(randomly_ordered_instances_file)
        else:
            self.make_randomly_ordered_instances()

        #print "randomly ordered instances", self.randomly_ordered_instances

        self.instances = self.make_instances()

    def get_n_for_inputs_with_length(self):
        n_for_inputs_with_length = collections.defaultdict(list)
        for n, input in enumerate(self.inputs):
            if self.dataset == "e2e":
                separator = ","
            elif self.dataset == "webnlg":
                separator = "]),"
            l = len(input.split(separator))
            n_for_inputs_with_length[l].append(n)
        return n_for_inputs_with_length

    def read_lines(self, file):
        with open(file) as f:
            return [l.decode("utf-8").strip().lower() for l in f.readlines()]

    def make_randomly_ordered_instances(self):
        self.randomly_ordered_instances = {}
        for (num_inputs, num_instances) in self.inputs_with_num_instances:
            instances = range(0, num_instances)
            random.shuffle(instances)
            self.randomly_ordered_instances[num_inputs] = instances

    def write_randomly_ordered_instances(self, outfile):
        with open(outfile, "w") as of:
            for l in sorted(self.randomly_ordered_instances):
                randomly_ordered_instances = [str(i) for i in self.randomly_ordered_instances[l]]
                of.write("%d: %s\n" %(l, ", ".join(randomly_ordered_instances)))

    def read_ranomly_ordered_instances(self, infile):
        self.randomly_ordered_instances = {}
        lines = self.read_lines(infile)
        for line in lines:
            l, randomly_ordered_instances = line.split(": ")
            self.randomly_ordered_instances[int(l)] = [int(n) for n in randomly_ordered_instances.split(", ")]

    def make_instances(self):
        instances = []
        for (num_inputs, num_instances) in self.inputs_with_num_instances:
            for n, random_order_n in zip(range(0, num_instances), self.randomly_ordered_instances[num_inputs]):
                print "num inputs: %d, num instances: %d, n: %d, random order n: %d" %(num_inputs, num_instances, n, random_order_n)
                n_in_src_tgt_list = self.n_for_inputs_with_length[num_inputs][n]
                src = self.inputs[n_in_src_tgt_list]
                tgt = self.targets[n_in_src_tgt_list]
                instances.append(NLGDataInstance(n_in_src_tgt_list, n, random_order_n, num_inputs, self.modelname, src, tgt, ""))
        return instances

    def get_instances(self, start, n_per_length):
        selected_instances = []
        # group instances according to num_inputs
        get_num_inputs = operator.attrgetter('num_inputs')
        instances_by_length = [list(g) for k, g in itertools.groupby(sorted(self.instances, key=get_num_inputs), get_num_inputs)]

        # sort instances in each group according to random_order_n
        for insts in instances_by_length:
            sorted_instances = sorted(insts, key=operator.attrgetter('random_order_n'))
            selected_instances.extend(sorted_instances[start:n_per_length])
        # print "selected instances", selected_instances
        return selected_instances

    @staticmethod
    def group_by_src(instances):
        get_n_global = operator.attrgetter('n_global')
        instances_by_src = [list(g) for k, g in
                               itertools.groupby(sorted(instances, key=get_n_global), get_n_global)]

        instances_with_multiple_targets = []
        for insts_with_same_src in instances_by_src:
            insts_with_same_src = sorted(insts_with_same_src, key=operator.attrgetter('model'))
            tgts = [inst.tgt[0] for inst in insts_with_same_src]
            inst = insts_with_same_src[0]
            inst.set_tgts(tgts)
            instances_with_multiple_targets.append(inst)

        return instances_with_multiple_targets


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=["e2e", "webnlg"])
    parser.add_argument("src_file")
    parser.add_argument("tgt_file")
    parser.add_argument("modelname")
    parser.add_argument("randomly_ordered_instances_file")
    parser.add_argument("outfolder")
    parser.add_argument("--tgt_file_2", default = None)
    parser.add_argument("--modelname_2", default = None)
    parser.add_argument("--group_by_src", action="store_true")

    random.seed(1234)
    args = parser.parse_args()
    start_data_instances = 0
    end_data_instances = 10

    data = NLGData(args.dataset, args.src_file, args.tgt_file, args.modelname, args.randomly_ordered_instances_file)
    data.write_randomly_ordered_instances(args.randomly_ordered_instances_file)
    instances = data.get_instances(start_data_instances, end_data_instances)

    if args.tgt_file_2:
        data_2 = NLGData(args.dataset, args.src_file, args.tgt_file_2, args.modelname_2, args.randomly_ordered_instances_file)
        instances.extend(data_2.get_instances(start_data_instances, end_data_instances))

    random.shuffle(instances)

    if args.group_by_src:
        instances = NLGData.group_by_src(instances)
    instances_to_annotate_file = os.path.join(args.outfolder,
                                              "instances_to_annotate_%d-%d.csv" %(start_data_instances, end_data_instances))
    instances_to_analyze_file = os.path.join(args.outfolder,
                                             "instances_to_analyze_%d-%d.csv" %(start_data_instances, end_data_instances))
    with open(instances_to_annotate_file, "w") as to_annotate_file, open(instances_to_analyze_file, "w") as to_analyze_file:
        for i, instance in enumerate(instances):
            instance.set_id(i)
            to_annotate_file.write(instance.as_str_to_annotate())
            to_analyze_file.write(instance.as_str_to_analyze())



