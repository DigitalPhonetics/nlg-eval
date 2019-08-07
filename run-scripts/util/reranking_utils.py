import argparse

def strip_list_entries(list_):
    return [item.strip() for item in list_]


def create_input_output_files_hypotheses(src, tgt_hypotheses, src_out, tgt_out, tgt_scores_out, hypotheses_counter):
    """
    src: one input per line
    tgt_hypotheses: one output + score separated by tab per line,
                    multiple hypotheses for one input separated by empty line
    creates
    - src_out: repeats each line in src as many times as there are hypotheses
    - tgt_out: hypotheses from hypotheses_tgt without empty lines
    - tgt_scores_out: scores from hypotheses_tgt without empty lines
    - hypotheses_counter: number of hypotheses for each input, as many lines as src
    """
    with open(src, "r") as sf:
        inputs = sf.readlines()
    inputs = strip_list_entries(inputs)

    targets = []
    hypotheses_for_input = []
    scores = []
    scores_for_input = []
    with open(tgt_hypotheses) as tf:
        for line in tf.readlines():
            if not line.strip():
                targets.append(hypotheses_for_input)
                hypotheses_for_input = []
                scores.append(scores_for_input)
                scores_for_input = []
            else:
                print line
                target, score = line.split("\t")
                score = score.strip()
                hypotheses_for_input.append(target)
                scores_for_input.append(str(score))

    with open(src_out, "w") as so, open(tgt_out, "w") as to, open(tgt_scores_out, "w") as tso,\
            open(hypotheses_counter, "w") as ho:
        for i, hypotheses_for_input in enumerate(targets):
            num_hypotheses = len(hypotheses_for_input)
            so.write("\n".join([inputs[i]] * num_hypotheses) + "\n")
            to.write("\n".join(hypotheses_for_input) + "\n")
            tso.write("\n".join(scores[i]) + "\n")
            ho.write(str(num_hypotheses)+"\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', action='store', help='Path to input file')
    parser.add_argument('-tgt_hypotheses', action='store', help='Path to file with target hypotheses')
    parser.add_argument('-src_out', action='store')
    parser.add_argument('-tgt_out', action='store')
    parser.add_argument('-tgt_scores_out', action='store')
    parser.add_argument('-hypotheses_counter_out', action='store')

    args = parser.parse_args()

    create_input_output_files_hypotheses(args.src, args.tgt_hypotheses, args.src_out, args.tgt_out,
                                         args.tgt_scores_out, args.hypotheses_counter_out)




