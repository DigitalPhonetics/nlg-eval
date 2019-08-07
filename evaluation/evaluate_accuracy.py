import sys

def read_file(fname):
    with open(fname) as f:
        return [l.strip() for l in f.readlines()]

def word_accuracy(pred, ref):
    pred_tokens = pred.split()
    ref_tokens = ref.split()
    correct = 0
    for p, r in zip(pred_tokens, ref_tokens):
        if p == r:
            correct += 1

    tokens = min(len(pred_tokens), len(ref_tokens))
    return correct, tokens, correct/float(tokens) * 100

def accuracy_two_refs(preds, refs1, refs2):
    correct = 0
    tokens = 0
    macro_acc = 0
    insts = len(preds)
    completely_correct_predictions = 0
    incorrect_instances = []
    evaluated_preds = []

    for i, (pred, ref1, ref2) in enumerate(zip(preds, refs1, refs2)):
        template = 0
        if pred == ref1:
            completely_correct_predictions += 1
            template = 1
        elif pred == ref2:
            completely_correct_predictions += 1
            template = 2
        else:
            incorrect_instances.append((i, pred, ref1))
        evaluated_preds.append((pred, template))

        correct1, tokens1, acc1 = word_accuracy(pred, ref1)
        correct2, tokens2, acc2 = word_accuracy(pred, ref2)

        if acc1 > acc2:
            correct += correct1
            tokens += tokens1
            macro_acc += acc1
        else:
            correct += correct2
            tokens += tokens2
            macro_acc += acc2

    print "%d instances" %insts, "%d completely correct predictions" %completely_correct_predictions
    print "# macro acc\t%.2f" %(macro_acc / insts)
    print "# micro acc\t%.2f" %(correct / float(tokens) * 100)
    print "# completely correct predictions\t%.2f" %(completely_correct_predictions / float(insts) * 100)

    print "incorrect instances"
    for i, pred, ref in incorrect_instances:
        print "instance %d:\np:\t%sg:\t\n%s" %(i, pred, ref)

    print "evaluated instances"
    #for i, (pred, template) in enumerate(evaluated_preds):
    #    print "%s;%s" %(pred, template)

def accuracy(preds, refs):
    correct = 0
    tokens = 0
    macro_acc = 0
    insts = len(preds)
    completely_correct_predictions = 0
    incorrect_instances = []

    for i, (pred, ref) in enumerate(zip(preds, refs)):
        if pred == ref:
            completely_correct_predictions += 1
        else:
            incorrect_instances.append((i, pred, ref))
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        curr_correct = 0
        for p, r in zip(pred_tokens, ref_tokens):
            if p == r:
                curr_correct += 1
        correct += curr_correct
        curr_tokens = min(len(pred_tokens), len(ref_tokens))
        tokens += curr_tokens
        curr_acc = curr_correct / float(curr_tokens) * 100
        macro_acc += curr_acc

    print "# macro acc\t%.2f" %(macro_acc / insts)
    print "# micro acc\t%.2f" %(correct / float(tokens) * 100)
    print "# completely correct predictions\t%.2f" %(completely_correct_predictions / float(insts) * 100)

    print "incorrect instances"
    for i, pred, ref in incorrect_instances:
        print "instance %d:\n%s\n%s" %(i, pred, ref)

prediction = sys.argv[1]
reference = sys.argv[2]
pred_lines = read_file(prediction)
ref_lines = read_file(reference)

if len (sys.argv) == 4:
    print "evaluate with 2 reference files"
    reference2 = sys.argv[3]
    ref_lines2 = read_file(reference2)
    accuracy_two_refs(pred_lines, ref_lines, ref_lines2)

else:
    accuracy(pred_lines, ref_lines)