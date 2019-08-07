import argparse
import input
import detokenizer

def read_lines(file):
    with open(file, "r") as f:
        lines = [l.decode("utf-8").strip() for l in f.readlines()]
    return lines

def write_lines(lines, outfile):
    with open(outfile, "w") as f:
        for line in lines:
            f.write("%s\n" %line.encode("utf-8"))

def restore_output_character_based(lines):
    joined_lines = []
    for line in lines:
        line = line.strip()
        line = line.replace("   ", "<NEW-WORD>")
        line = line.replace(" ", "")
        line = line.replace("<NEW-WORD>", " ")
        joined_lines.append(line)
    return joined_lines

def parse_relex_line(line):
    delex_lex_tgt_mapping = {}
    if line: # do nothing for empty relexicalization lines
        delex_triples = line.split(input.Input.RELEX_ENTRIES_SEPARATOR)
        for delex_triple in delex_triples:
            if delex_triple:
                delex, lex_src, lex_tgt = delex_triple.split(input.Input.RELEX_ENTRIES_FIELD_SEPARATOR)
                delex_lex_tgt_mapping[delex] = lex_tgt

    return delex_lex_tgt_mapping

def relexicalize(lines, relex_lines):
    relexicalized_lines = []
    for line, relex_line in zip(lines, relex_lines):
        delex_lex_mapping = parse_relex_line(relex_line)
        # print "delexicalized line", line
        # print "delex_lex_mapping", str(delex_lex_mapping)
        for delex in delex_lex_mapping:
            line = line.replace(delex, delex_lex_mapping[delex])
        relexicalized_lines.append(line)
        # print "lexicalized line", line

    return relexicalized_lines


def detokenize(lines):
    detokenized_lines = []
    detok = detokenizer.Detokenizer()
    for line in lines:
        detokenized_lines.append(detok.detokenize(line))

    return detokenized_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', action='store', help='Path to dataset file')
    parser.add_argument('preprocessing_type', choices=['character', "character-delex", "subword", "word", "word-delex"],
                        help='Type of preprocessing which was applied to this file')
    parser.add_argument('output_path', help='Path to common format output dataset')
    parser.add_argument('--relexicalization_file', help='File to load relexicalization information from')
    parser.add_argument('--log-level', dest='log_level',
                        default='info',
                        help='Logging level')

    args = parser.parse_args()
    lines = read_lines(args.file_path)

    if args.preprocessing_type == "character":
        lines = restore_output_character_based(lines)

    if "delex" in args.preprocessing_type:
        relex_lines = read_lines(args.relexicalization_file)
        lines = relexicalize(lines, relex_lines)

    if "word" in args.preprocessing_type:
        lines = detokenize(lines)

    write_lines(lines, args.output_path)

