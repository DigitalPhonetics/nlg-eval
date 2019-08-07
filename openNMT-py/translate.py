#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals
import os
import argparse
import math
import codecs
import torch
from itertools import count
import collections
import numpy as np

import onmt.io
import onmt.translate
import onmt
import onmt.ModelConstructor
import onmt.modules
import opts

parser = argparse.ArgumentParser(
    description='translate.py',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
opts.add_md_help_argument(parser)
opts.translate_opts(parser)

opt = parser.parse_args()

opts.print_set_options(opt)


def _report_score(name, score_total, words_total):
    print("%s AVG SCORE: %.4f, %s PPL: %.4f" % (
        name, score_total / words_total,
        name, math.exp(-score_total / words_total)))


def _report_bleu():
    import subprocess
    print()
    res = subprocess.check_output(
        "perl tools/multi-bleu.perl %s < %s" % (opt.tgt, opt.output),
        shell=True).decode("utf-8")
    print(">> " + res.strip())


def _report_rouge():
    import subprocess
    res = subprocess.check_output(
        "python tools/test_rouge.py -r %s -c %s" % (opt.tgt, opt.output),
        shell=True).decode("utf-8")
    print(res.strip())


def get_src_tgt_sequence_join_character(symbol_representation):
    if symbol_representation == "word2word":
        src_sequence_join_character = u" "
        tgt_sequence_join_character = u" "
    elif symbol_representation == "char2char":
        src_sequence_join_character = u""
        tgt_sequence_join_character = u""
    elif symbol_representation == "word2char":
        src_sequence_join_character = u" "
        tgt_sequence_join_character = u""

    return src_sequence_join_character, tgt_sequence_join_character


def main():
    dummy_parser = argparse.ArgumentParser(description='train.py')
    opts.model_opts(dummy_parser)
    dummy_opt = dummy_parser.parse_known_args([])[0]

    opt.cuda = opt.gpu > -1
    if opt.cuda:
        torch.cuda.set_device(opt.gpu)

    # Load the model.
    fields, model, model_opt = \
        onmt.ModelConstructor.load_test_model(opt, dummy_opt.__dict__)

    # File to write sentences to.
    out_file = codecs.open(opt.output, 'w', 'utf-8')

    # Test data
    data = onmt.io.build_dataset(fields, opt.data_type,
                                 opt.src, opt.tgt,
                                 src_dir=opt.src_dir,
                                 sample_rate=opt.sample_rate,
                                 window_size=opt.window_size,
                                 window_stride=opt.window_stride,
                                 window=opt.window,
                                 use_filter_pred=False,
                                 symbol_representation=opt.symbol_representation,
                                 revert_targets=opt.revert_targets)

    # Sort batch by decreasing lengths of sentence required by pytorch.
    # sort=False means "Use dataset's sortkey instead of iterator's".
    data_iter = onmt.io.OrderedIterator(
        dataset=data, device=opt.gpu,
        batch_size=opt.batch_size, train=False, sort=False,
        sort_within_batch=True, shuffle=False)

    # Translator
    scorer = onmt.translate.GNMTGlobalScorer(opt.alpha, opt.beta)
    translator = onmt.translate.Translator(model, fields,
                                           beam_size=opt.beam_size,
                                           n_best=opt.n_best,
                                           global_scorer=scorer,
                                           max_length=opt.max_length,
                                           copy_attn=model_opt.copy_attn,
                                           cuda=opt.cuda,
                                           beam_trace=opt.dump_beam != "",
                                           min_length=opt.min_length)
    builder = onmt.translate.TranslationBuilder(
        data, translator.fields,
        opt.n_best, opt.replace_unk, opt.tgt)

    # Statistics
    counter = count(1)
    pred_score_total, pred_words_total = 0, 0
    gold_score_total, gold_words_total = 0, 0

    src_sequence_join_character, tgt_sequence_join_character = get_src_tgt_sequence_join_character(
        opt.symbol_representation)

    # convert number of variations that should be created for each input to int
    # default is n_best hypotheses per input
    num_variations_for_input = collections.defaultdict(lambda: opt.n_best)
    if opt.num_variations:
        for i, v in enumerate(opt.num_variations.split(",")):
            num_variations_for_input[i] = int(v)
    print "%s variations per input" % str(num_variations_for_input)

    input_counter = 0

    for batch in data_iter:
        batch_data = translator.translate_batch(batch, data)
        translations = builder.from_batch(batch_data)

        for trans in translations:
            pred_score_total += trans.pred_scores[0]
            pred_words_total += len(trans.pred_sents[0])
            n_best_pred_scores = trans.pred_scores[:opt.n_best]
            if opt.tgt:
                gold_score_total += trans.gold_score
                gold_words_total += len(trans.gold_sent)

            if opt.revert_targets:
                n_best_preds = [tgt_sequence_join_character.join(reversed(pred))
                                for pred in trans.pred_sents[:opt.n_best]]
            else:
                n_best_preds = [tgt_sequence_join_character.join(pred)
                                for pred in trans.pred_sents[:opt.n_best]]

            # provide src
            if opt.verbose:
                out_file.write("input:\t" + src_sequence_join_character.join(trans.src_raw) + "\n")
                n_best_preds = ["hyp %d:\t%s" % (i, pred) for i, pred in enumerate(n_best_preds)]

            n_best_preds = [pred.strip().replace("\n", " ") for pred in n_best_preds]

            num_variations = num_variations_for_input[input_counter]

            # fill up if fewer hypotheses were returned by beam search than required number of variations
            if len(n_best_preds) < num_variations:
                num_preds_to_add = num_variations - len(n_best_preds)
                n_best_preds.extend(
                    n_best_preds[i % len(n_best_preds)] for i in range(0, num_preds_to_add))
                n_best_pred_scores.extend(
                    n_best_pred_scores[i % len(n_best_preds)] for i in range(0, num_preds_to_add))

            if opt.stochastic:
                preds = np.random.choice(n_best_preds, num_variations, replace=False)
            else:
                preds = n_best_preds[:num_variations]

            if opt.report_individual_scores:
                preds_and_scores = []
                for (pred, pred_score) in zip(preds, n_best_pred_scores):
                    preds_and_scores.append("\t".join([pred.strip(), str(pred_score)]))
                preds = n_best_preds_and_scores

            out_file.write('\n'.join(preds) + "\n")
            if opt.n_best > 1:
                out_file.write('\n')

            if opt.verbose:
                sent_number = next(counter)
                output = trans.log(sent_number)
                os.write(1, output.encode('utf-8'))

            input_counter += 1

    _report_score('PRED', pred_score_total, pred_words_total)
    if opt.tgt:
        _report_score('GOLD', gold_score_total, gold_words_total)
        if opt.report_bleu:
            _report_bleu()
        if opt.report_rouge:
            _report_rouge()

    if opt.dump_beam:
        import json
        json.dump(translator.beam_accum,
                  codecs.open(opt.dump_beam, 'w', 'utf-8'))


if __name__ == "__main__":
    main()
