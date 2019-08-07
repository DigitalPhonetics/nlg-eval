import sys
import os
import random

def read_refs(reference_file):
    max_num_refs = 0
    refs = []
    all_refs = []
    with open(reference_file) as references:
        for line in references:
            if line != '\n':
                refs.append(line.strip())
            else:
                all_refs.append(refs)
                if len(refs) > max_num_refs:
                    max_num_refs = len(refs)
                refs = []

    print "max num refs: %d" %(max_num_refs)
    return all_refs, max_num_refs

def filter_refs(all_refs):
    return [refs for refs in all_refs if len(refs) > 1]

def get_pred_and_references(refs, index):
    # modulo: start again at first ref if index is > than number of references
    pred_index = index %len(refs)
    # prediction = ref at this index
    # references: all other refs
    return refs[pred_index], refs[:pred_index] + refs[pred_index+1:]

def write_new_pred_and_references_files(outfolder, all_refs, max_num_refs):
    for index in range(0, max_num_refs):
        with open(os.path.join(outfolder, "%d_as_predictions.txt" %index),"w") as new_prediction_file,\
                open(os.path.join(outfolder, "%d_references.txt" %index),"w") as new_references_file:
            for refs in all_refs:
                pred, references = get_pred_and_references(refs, index)
                new_prediction_file.write(pred + "\n")
                new_references_file.write("\n".join(references) + "\n\n")

def get_random_eval_indices():
    """
    return indices of reference files to evaluate automatic predictions against
    to have fair comparison between human eval and automatic predictions (same number of references)
    :return:
    """
    e2e_eval_indices = [random.randint(0, 42) for p in range(0, 10)]
    print "e2e eval indices", e2e_eval_indices
    webnlg_eval_indices = [random.randint(0, 7) for p in range(0, 10)]
    print "webnlg eval indices", webnlg_eval_indices

if __name__ == "__main__":
    random.seed(1234)
    get_random_eval_indices()

    reference_file = sys.argv[1]
    outfolder = sys.argv[2]

    all_refs, max_num_refs = read_refs(reference_file)
    print "%d instances" %len(all_refs)

    # print the indices of filtered instances, already in the format for sed
    filtered_insts = [str(i+1) + "d" for i, refs in enumerate(all_refs) if len(refs) < 2]
    print "%d filtered instances %s" %(len(filtered_insts), ";".join(filtered_insts))

    all_refs = filter_refs(all_refs)
    print "%d instances with at least 2 references" % len(all_refs)
    write_new_pred_and_references_files(outfolder, all_refs, max_num_refs)