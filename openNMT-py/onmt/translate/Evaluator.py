import torch
from torch.autograd import Variable

import onmt.translate.Beam
import onmt.io


class Evaluator(object):
    """
    Computes the probability of sentences under the given model


    Args:
       model (:obj:`onmt.modules.NMTModel`):
          NMT model to use for translation
       fields (dict of Fields): data fields
       global_scores (:obj:`GlobalScorer`):
         object to rescore final translations
       copy_attn (bool): use copy attention during translation
       cuda (bool): use cuda
    """
    def __init__(self, model, fields,
                 global_scorer=None, copy_attn=False, cuda=False):
        self.model = model
        self.fields = fields
        self.global_scorer = global_scorer
        self.copy_attn = copy_attn
        self.cuda = cuda

    # def evaluate_batch(self, batch, data):
    #
    #
    #     # (0) Prep each of the components of the search.
    #     # And helper method for reducing verbosity.
    #     batch_size = batch.batch_size
    #     data_type = data.data_type
    #     vocab = self.fields["tgt"].vocab
    #
    #     # Help functions for working with beams and batches
    #     def var(a): return Variable(a, volatile=True)
    #
    #     def rvar(a): return var(a.repeat(1, beam_size, 1))
    #
    #     def bottle(m):
    #         return m.view(batch_size * beam_size, -1)
    #
    #     def unbottle(m):
    #         return m.view(beam_size, batch_size, -1)
    #
    #     # (1) Run the encoder on the src.
    #     src = onmt.io.make_features(batch, 'src', data_type)
    #     src_lengths = None
    #     if data_type == 'text':
    #         _, src_lengths = batch.src
    #
    #     enc_states, context = self.model.encoder(src, src_lengths)
    #     dec_states = self.model.decoder.init_decoder_state(
    #                                     src, context, enc_states)
    #
    #     if src_lengths is None:
    #         src_lengths = torch.Tensor(batch_size).type_as(context.data)\
    #                                               .long()\
    #                                               .fill_(context.size(0))
    #
    #     # (4) Extract sentences from beam.
    #     ret = {}
    #     ret["gold_score"] = [0] * batch_size
    #     ret["gold_score"] = self._run_target(batch, data)
    #     ret["batch"] = batch
    #     return ret

    def evaluate_batch(self, batch, data):
        """
        Evaluate the probability of a batch of sentences.

        Args:
           batch (:obj:`Batch`): a batch from a dataset object
           data (:obj:`Dataset`): the dataset object

        Todo:
           Shouldn't need the original dataset.
        """

        data_type = data.data_type
        if data_type == 'text':
            _, src_lengths = batch.src
        else:
            src_lengths = None
        src = onmt.io.make_features(batch, 'src', data_type)
        tgt_in = onmt.io.make_features(batch, 'tgt')[:-1]

        #  (1) run the encoder on the src
        enc_states, context = self.model.encoder(src, src_lengths)
        dec_states = self.model.decoder.init_decoder_state(src,
                                                           context, enc_states)

        #  (2) if a target is specified, compute the 'goldScore'
        #  (i.e. log likelihood) of the target under the model
        tt = torch.cuda if self.cuda else torch
        gold_scores = tt.FloatTensor(batch.batch_size).fill_(0)
        dec_out, dec_states, attn = self.model.decoder(
            tgt_in, context, dec_states, context_lengths=src_lengths)

        tgt_pad = self.fields["tgt"].vocab.stoi[onmt.io.PAD_WORD]
        for dec, tgt in zip(dec_out, batch.tgt[1:].data):
            # Log prob of each word.
            out = self.model.generator.forward(dec)
            tgt = tgt.unsqueeze(1)
            scores = out.data.gather(1, tgt)
            scores.masked_fill_(tgt.eq(tgt_pad), 0)
            gold_scores += scores
        return gold_scores
