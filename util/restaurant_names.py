import sys
import numpy
import re
import random


def read_lines(fname):
    with open(fname, "r") as f:
        return [l.lower().strip() for l in f.readlines()]


def write_lines(lines, f):
    with open(f, "w") as out:
        out.write("\n".join(lines))


def analyze_restaurant_file(fname):
    restaurants = read_lines(fname)

    # unique restaurants
    restaurants = sorted(set(restaurants))
    print "%d unique lowercased restaurants" % len(restaurants)

    tokenized_restaurants = [r.split() for r in restaurants]

    num_tokens = [len(r) for r in tokenized_restaurants]
    num_chars = [len(r) for r in restaurants]
    num_chars_per_token = [len(t) for r in tokenized_restaurants for t in r]

    print "average number of tokens\t%.4f" % numpy.mean(num_tokens, axis=0)
    print "stdev number of tokens\t%.4f" % numpy.std(num_tokens, axis=0)
    print "average number of characters\t%.4f" % numpy.mean(num_chars, axis=0)
    print "stdev number of characters\t%.4f" % numpy.std(num_chars, axis=0)
    print "average number of chars per token\t%.4f" % numpy.mean(num_chars_per_token, axis=0)
    print "stdev number of chars per token\t%.4f" % numpy.std(num_chars_per_token, axis=0)

    return restaurants


def replace_slot_values(instances, values, slot):
    modified_instances = []
    for c, inst in enumerate(instances):
        # wrap around: if all values have been used, start again at beginning (handled by modulo operator)
        new_value = values[c % len(values)]
        modified_instance = re.sub(r"%s\[.*?\]" % slot, "%s[%s]" % (slot, new_value), inst)

        modified_instances.append(modified_instance)

    return modified_instances


def replace_restaurant_names(restaurant_file, dataset_file):
    # replace restaurant names in csv dataset instances

    instances = read_lines(dataset_file)
    restaurants = read_lines(restaurant_file)

    instances = replace_slot_values(instances, restaurants, "name")
    random.shuffle(restaurants)
    instances = replace_slot_values(instances, restaurants, "near")

    write_lines(instances, dataset_file + "_name_near_replaced_no_original_test_names")


if __name__ == "__main__":
    random.seed(0)
    restaurant_file = sys.argv[1]
    # csv file
    dataset_file = sys.argv[2]

    # get statistics on restaurant names
    # restaurants = analyze_restaurant_file(restaurant_file)
    # write_lines(restaurants, "restaurant_names.txt")

    replace_restaurant_names(restaurant_file, dataset_file)
