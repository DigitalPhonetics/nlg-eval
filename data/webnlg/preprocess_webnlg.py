"""
convert WebNLG data to complete training, dev, test files
target directory structure:
data
    train   -> subfolder 1triples, 2triples, ...
    dev     -> subfolder 1triples, 2triples, ...
    test    -> testdata_unseen_with_lex.xml
"""
import os
import xml.etree.ElementTree as ET
import argparse

def webNLG2singleFile(dir, outfile, mode):
    """

    :param dir:
    :param outfile:
    :param mode: singleref, multiref
    :return:
    """
    instances = [] # list of db, text pairs

    # loop over all files in subdirs
    for subdir, dirs, files in os.walk(dir):
        for f in files:
            tree = ET.parse(os.path.join(subdir, f))
            root = tree.getroot()
            for index, elem in enumerate(root.iter('entry')):
                # elem.text elem.tag
                cat = elem.attrib["category"].encode('utf-8')
                #print "category", cat

                # have multiple mtriples for one entry!
                db = []
                for idx, db_elem in enumerate(elem.iter('mtriple')):
                    # do some cleaning of the triples:
                    try:
                        triple = db_elem.text.encode('utf-8')
                    except:
                        print f, db_elem.text
                    triple = triple.strip()
                    db.append(triple)

                db = "<NEW-TRIPLE>".join(db)

                # create instances
                if mode == "singleref":
                    for idx, txt_elem in enumerate(elem.iter('lex')):
                        instances.append((cat, db, txt_elem.text.encode('utf-8')))
                        #print db, txt_elem.text

                if mode == "multiref":
                    references = []
                    for idx, txt_elem in enumerate(elem.iter('lex')):
                        references.append(txt_elem.text.encode('utf-8'))
                    instances.append((cat, db, references))

    if mode == "singleref":
        with open(outfile + ".txt", "w") as outf:
            for (cat, db, text) in instances:
                outf.write(cat + "\t" + db + "\t" + text + "\n")

    elif mode == "multiref":
        with open(outfile + "_triples.txt", "w") as outf_triples,  open(outfile + "_references.txt", "w") as outf_references:
            for (cat, db, references) in instances:
                outf_triples.write(cat + "\t"+ db + "\n")
                for reference in references:
                    outf_references.write(reference + "\n")
                outf_references.write("\n")

if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help = "path to subdirectory in data folder containing the original WebNLG files")
    parser.add_argument("output_file_base", help="output file name (.txt or _triples.txt/_references.txt will be appended")
    parser.add_argument("mode", choices=["singleref", "multiref"], help="use single-ref for creating training and development, multi-ref for creating evaluation files")

    args = parser.parse_args()
    webNLG2singleFile(args.data_dir, args.output_file_base, args.mode)



