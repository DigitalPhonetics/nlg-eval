#!/usr/bin/env python

from __future__ import division, unicode_literals
import os
import argparse
import math
import codecs
import torch

from itertools import count

import onmt.io
import onmt.translate
import onmt
import onmt.ModelConstructor
import onmt.modules
import opts

parser = argparse.ArgumentParser(
    description='evaluate.py',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
opts.add_md_help_argument(parser)
opts.translate_opts(parser)

opt = parser.parse_args()

opts.print_set_options(opt)

def _report_score(name, score_total, words_total):
    print("%s AVG SCORE: %.4f, %s PPL: %.4f" % (
        name, score_total / words_total,
        name, math.exp(-score_total / words_total)))

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

    # File to write scores to.
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

    # Evaluator
    scorer = onmt.translate.GNMTGlobalScorer(opt.alpha, opt.beta)
    evaluator = onmt.translate.Evaluator(model, fields, scorer,
                                           copy_attn=model_opt.copy_attn,
                                           cuda=opt.cuda)

    # Statistics
    #counter = count(1)
    #score_total, words_total = 0, 0

    for batch in data_iter:
        scores = evaluator.evaluate_batch(batch, data)
        for score in scores:
            out_file.write(str(score))
            out_file.write('\n')
            out_file.flush()

            #if opt.verbose:
            #    sent_number = next(counter)
            #    output = trans.log(sent_number)
            #    os.write(1, output.encode('utf-8'))

if __name__ == "__main__":
    main()
