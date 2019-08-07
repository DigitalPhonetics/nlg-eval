from targets import Targets
import re



def matches_input(input, string_to_delex, only_delex_value):
    """
    :param input:
    :param string_to_delex:
    :param only_delex_value: only try to delexicalize the value field of each record, else try all
    :return:
    """
    for record in input.records:
        if string_to_delex in record.value:
            return True

        if not only_delex_value:
            if string_to_delex in record.type:
                return True

            if string_to_delex in record.entity:
                return True

    return False

def matches_targets(targets, string_to_delex):
    for target in targets:
        if string_to_delex in target:
            return True
    return False

def delexicalize_instance_with_targets(input, targets, delex_candidates, only_delex_value, force_delex_source):
    """
    :param input:
    :param targets:
    :param delex_candidates:
    :param only_delex_value:
    :param force_delex_source: always delexicalize source, even if the delexicalized string cannot be matched in the target
    :return:
    """
    delex_dict = {}
    relex_dict = {}
    #print "delexicalize instance with targets", delex_candidates, "force delex source is", force_delex_source
    for cand in delex_candidates:

        # delexicalize source
        string_to_delex_src = cand
        delex_string = input.delex_dict.get(cand)
        input.delexicalize(cand)

        # delexicalize target if possible
        matched_target_substring = targets.match_string_to_delexicalize(cand)
        string_to_delex_tgt = matched_target_substring

        if matched_target_substring:
            targets.delexicalize(string_to_delex_tgt, delex_string)
        else:
            string_to_delex_tgt = string_to_delex_src

        delex_dict[string_to_delex_src] = delex_string
        relex_dict[delex_string] = (string_to_delex_src, string_to_delex_tgt)

    input.delex_dict = delex_dict
    input.relex_dict = relex_dict

    return input, targets

def delexicalize_instance_without_targets(input, delex_candidates, only_delex_value):
    delex_dict = {}
    relex_dict = {}
    for cand in delex_candidates:
        if matches_input(input, cand, only_delex_value):
            string_to_delex_src = cand
            delex_string = input.delex_dict.get(cand)
            input.delexicalize()
            delex_dict[string_to_delex_src] = delex_string
            relex_dict[delex_string] = (string_to_delex_src, string_to_delex_src)

    input.delex_dict = delex_dict
    input.relex_dict = relex_dict

    return input


def delexicalize_instance(input, targets, only_delex_value, has_targets, force_delex_source):
    delex_candidates = input.get_delex_candidates()

    if has_targets:
        input, targets = delexicalize_instance_with_targets(input, targets, delex_candidates, only_delex_value, force_delex_source)
        return input, targets
    else:
        input = delexicalize_instance_without_targets(input, delex_candidates, only_delex_value)
        return input, Targets("")







