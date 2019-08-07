import argparse

class HypothesesSet(object):
    def __init__(self):
        pass


def strip_list_entries(list_):
    return [item.strip() for item in list_]

def convert_to_type(list_, type_):
    return [type_(item) for item in list_]


def read_lines(file_, type_=str):
    with open(file_) as f:
        lines = f.readlines()
    lines = strip_list_entries(lines)
    if type_ != str:
        lines = convert_to_type(lines, type_)
    return lines

def weight_scores(scores):
    # TODO assert that weights are of same length as scores
    weights = [1.0, 1.0]
    weighted_scores = []
    for i, score_type in enumerate(scores):
        score_type = [score * weights[i] for score in score_type]
        weighted_scores.append(score_type)
    return weighted_scores

def read_hypotheses_and_scores(hypotheses_file, scores_files):
    hypotheses = read_lines(hypotheses_file)

    all_score_types = [read_lines(score_file, float) for score_file in scores_files]

    assert all(len(scores) == len(hypotheses) for scores in all_score_types), \
        "each hypothesis must have a score of each score type"

    all_score_types = weight_scores(all_score_types)

    hypotheses_with_scores = []
    for i, hypothesis in enumerate(hypotheses):
        scores = [score_type[i] for score_type in all_score_types]
        hypotheses_with_scores.append((hypothesis, scores))

    return hypotheses_with_scores

def group_hypotheses(hypotheses_counter, hypotheses):
    hypotheses_per_instance = read_lines(hypotheses_counter, int)
    start = 0
    grouped_hypotheses = []
    for number_of_hypotheses in hypotheses_per_instance:
        end = start + int(number_of_hypotheses)
        grouped_hypotheses.append(hypotheses[start:end])
        start = end

    return grouped_hypotheses


def rerank_hypotheses(hypotheses):
    def sort_key(hypothesis):
        return -sum(hypothesis[1])

    return sorted(hypotheses, key=sort_key)

def rerank_grouped_hypotheses(grouped_hypotheses):
    return [rerank_hypotheses(hypotheses) for hypotheses in grouped_hypotheses]

def print_all_hypotheses(outfile, grouped_hypotheses):
    with open(outfile, "w") as of:
        for hypotheses in grouped_hypotheses:
            for hypothesis, scores in hypotheses:
                of.write(hypothesis + "\t".join([str(score) for score in scores]))
            of.write("\n")

def print_best_hypotheses(outfile, grouped_hypotheses):
    with open(outfile, "w") as of:
        for hypotheses in grouped_hypotheses:
            of.write(hypotheses[0][0] + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-hypotheses', action='store', help='Path to file with target hypotheses')
    parser.add_argument('-hypotheses_counter', action='store', help='File with of number of hypotheses per input')
    parser.add_argument('-scores', help='List of score files separated by comma, each with one score per line')
    parser.add_argument('-tgt_reranked_out', action='store', help="Reranked hypotheses and their accumulated scores")
    parser.add_argument('-tgt_best_out', action='store', help="Single best hypothesis after reranking for each input")

    args = parser.parse_args()

    scores = args.scores.split(",")
    hypotheses = read_hypotheses_and_scores(args.hypotheses, scores)
    grouped_hypotheses = group_hypotheses(args.hypotheses_counter, hypotheses)
    reranked_hypotheses = rerank_grouped_hypotheses(grouped_hypotheses)

    print_all_hypotheses(args.tgt_reranked_out, reranked_hypotheses)
    print_best_hypotheses(args.tgt_best_out, reranked_hypotheses)




