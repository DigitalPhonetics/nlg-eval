"""
partition entries from WebNLG corpus development split randomly into two parts
and writes them to a single xml file each
"""
import xml.etree.ElementTree as ET
import sys
import os
import random

def partition_corpus(dir):
    root_1 = ET.Element('benchmark')
    root_1_entries = ET.Element("entries")
    #root_1.append(ET.Element("entries"))
    root_2 = ET.Element('benchmark')
    #root_2.append(ET.Element("entries"))
    root_2_entries = ET.Element("entries")
    # loop over all files in subdirs
    for subdir, dirs, files in os.walk(dir):
        for f in files:
            # find out the category from the file name
            # do not need this, have cat in attribute

            tree = ET.parse(os.path.join(subdir, f))
            root = tree.getroot()
            for index, elem in enumerate(root.iter('entry')):
                x = random.random()
                add_to_1 = (x > 0.5)
                if add_to_1:
                    root_1_entries.append(elem)
                else:
                    root_2_entries.append(elem)

    root_1.append(root_1_entries)
    root_2.append(root_2_entries)

    return root_1, root_2

def write_corpus(xml_tree_root, outfile):
    tree = ET.ElementTree(xml_tree_root)
    tree.write(outfile, 'utf-8')



dir = sys.argv[1]
outfile_1 = sys.argv[2]
outfile_2 = sys.argv[3]
root_1, root_2 = partition_corpus(dir)
write_corpus(root_1, outfile_1)
write_corpus(root_2, outfile_2)

