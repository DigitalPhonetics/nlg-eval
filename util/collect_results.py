import argparse
import os
import re

class Statistics(object):
    def __init__(self):
        self.measures = {"BLEU" : 0.0, "NIST": 0.0, "METEOR": 0.0,
                         "ROUGE_L": 0.0, "CIDEr" : 0.0, "ratio": 0.0,
                         "epoch": 0, "Train accuracy": 0.0, "Train perplexity": 0.0,
                         "Validation accuracy": 0.0, "Validation perplexity": 0.0}

    @staticmethod
    def to_percent(val):
        return val * 100

    def set_value(self, name, val):
        self.measures[name] = float(val)

    def maybe_set_value(self, line):
        line = line.strip().split(": ")
        if line[0] in self.measures:
            name, val = line
            self.set_value(name, val)

    def __str__(self):

        return "%d & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f \\\\"\
               %(self.measures["epoch"], self.measures["Train accuracy"], self.measures["Train perplexity"],
                 self.measures["Validation accuracy"], self.measures["Validation perplexity"],
                 Statistics.to_percent(self.measures["BLEU"]), self.measures["NIST"],
                 Statistics.to_percent(self.measures["METEOR"]),
                 Statistics.to_percent(self.measures["ROUGE_L"]),
                 self.measures["CIDEr"], self.measures["ratio"])


def collect_eval_files(rootdir):
    eval_files = []
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if "_eval" in filename:
                filename_absolute = os.path.join(folder, filename)
                eval_files.append(filename_absolute)
    return eval_files

def parse_eval_and_train_files(eval_files):
    for eval_file in eval_files:
        stats = parse_eval_file(eval_file)

        # find the matching train file
        train_file = get_train_file(eval_file)
        if train_file:
            stats = parse_train_file(train_file, stats)

        print "%s&%s" % (eval_file, stats)

def parse_eval_file(eval_file):
    stats = Statistics()
    with open(eval_file, "r") as f:
        lines =  f.readlines()
        for line in lines:
            stats.maybe_set_value(line)

    return stats

def get_train_file(eval_file):

    eval_file_name = os.path.basename(eval_file)
    model_name = get_model_name(eval_file_name)

    basedir = os.path.dirname(eval_file)
    train_file = "train_%s.log" %model_name
    train_file = os.path.join(basedir, train_file)

    # print "train file", train_file

    if os.path.isfile(train_file):
        return train_file
    return None

def get_model_name(eval_file_name, character_based=False):
    """
    :param eval_file_name:
    :param character_based: character_based and word_based models have a bit different naming conventions for files
    :return:
    """
    webNLG = False
    if character_based:
        model_name = eval_file_name.replace("test_multi_ref_", "")
        model_name = model_name.replace("dev_multi_ref_", "")
        model_name = model_name.replace("test_", "")
        model_name = model_name.split("_hypotheses")[0]
        model_name = model_name.split("_")
        # remove beam size
        model_name = "_".join(model_name[1:])
    else:# webNLG: #webNLG, word-based
        model_name = eval_file_name.split(".txt_")[0]
        model_name = model_name.replace("test_multi_ref_", "")
        model_name = model_name.replace("dev_multi_ref_", "")
        model_name = model_name.replace("test_", "")
        model_name = model_name.replace("eval", "")
    if not webNLG:
        #model_name = eval_file_name.split(".txt_")[1]
        #model_name = model_name.replace("eval", "")
        model_name = model_name.split("_hypotheses")[0]
        model_name = model_name.split("_")
        # remove beam size
        model_name = "_".join(model_name[1:])
        model_name = "forward_%s" % model_name
    print "model name", model_name
    return model_name

def parse_train_file(train_file, stats):
    with open(train_file, "r") as f:
        lines = f.readlines()
        epoch = get_epoch(lines[-7])
        # print "epoch", lines[-7], epoch
        stats.set_value("epoch", epoch)
        for line in lines[-6:]:
            stats.maybe_set_value(line)
    return stats

def get_epoch(line):
    epoch = 0
    if line.startswith("Epoch"):
        epoch = re.match(r'Epoch\s+(\d+)', line)
        epoch = epoch.group(1)
    return epoch


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("rootdir")

    args = parser.parse_args()

    eval_files = collect_eval_files(args.rootdir)
    parse_eval_and_train_files(eval_files)



