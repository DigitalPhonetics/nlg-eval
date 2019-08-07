from tokenizer import sent_tokenize_return_string_and_length
import statistics
import random

class Targets(object):
    def __init__(self, targets):
        if type(targets) is list:
            self.targets = targets
        else:
            self.targets = [targets]

        self.targets = map(self.clean, self.targets)

        self.token_stats = statistics.Statistics("number of tokens")
        self.sentence_stats = statistics.Statistics("number of sentences")
        self.delexicalized = False


    def clean(self, target):
        target = target.replace("\n", " ")
        target = " ".join(target.split())
        return target

    @property
    def number_of_references(self):
        return len(self.targets)

    def as_string(self):
        return "\n".join(self.targets).encode("utf-8")

    def as_string_single_line(self):
        return "; ".join(self.targets).encode("utf-8")

    def matches(self, string):
        for target in self.targets:
            if string in target:
                return True
        return False

    def add_targets(self, target_objects):
        targets = map(self.clean, target_objects.targets)
        self.targets.extend(targets)
        self.targets = Targets._unique(self.targets)
        #TODO statistics do not reflect hat duplicate targets are conflated
        self.token_stats.update_from_statistics_object(target_objects.token_stats)
        self.sentence_stats.update_from_statistics_object(target_objects.sentence_stats)

    def delexicalize(self, string_to_delex, delex_string):
        # can be called multiple times
        delex_targets = []
        for target in self.targets:
            delex_target = target.replace(string_to_delex, delex_string)
            delex_targets.append(delex_target)

        self.targets = delex_targets

        self.delexicalized = True

    @staticmethod
    def _unique(list_):
        """
        order preserving unique
        :return:
        """
        seen = set()
        seen_add = seen.add
        unique_targets = []
        for target in list_:
            if target not in seen:
                seen_add(target)
                unique_targets.append(target)

        return unique_targets

    def lexicalize(self, relex_dict):
        targets = []
        for target in self.targets:
            for delex_string in relex_dict:
                if delex_string in target:
                    # relex_dict consists of tuples (string_to_delex_src, string_to_delex_tgt)
                    lex_string = relex_dict[delex_string][1]
                    target = target.replace(delex_string, lex_string)
            targets.append(target)

        self.targets = targets
        self.delexicalized = False

    def tokenize(self):
        tokenized_targets = []
        for target in self.targets:
            target, num_sents, num_tokens = sent_tokenize_return_string_and_length(target)
            tokenized_targets.append(target)

            self.token_stats.update(num_tokens)
            self.sentence_stats.update(num_sents)

        self.targets = tokenized_targets

    def lowercase(self):
        lowercased_targets = []
        for target in self.targets:
            target = target.lower()
            lowercased_targets.append(target)
        self.targets = lowercased_targets

    def match_string_to_delexicalize(self, string_to_delex):
        # print "try to match %s" %string_to_delex.encode("utf-8")
        for target in self.targets:
            if string_to_delex in target:
                return string_to_delex
        return ""

    def random_target(self):
        return random.choice(self.targets).encode("utf-8")

    def first_target(self):
        return self.targets[0].encode("utf-8")

    def longest_target(self):
        return sorted(self.targets, key=len, reverse=True)[0].encode("utf-8")

    def shortest_target(self):
        return sorted(self.targets, key=len)[0].encode("utf-8")