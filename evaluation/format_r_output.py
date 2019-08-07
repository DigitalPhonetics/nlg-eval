import sys

def read_file(fname):
    with open(fname) as f:
        return [l.strip() for l in f.readlines()]

def format_output(lines):
    category = None
    i = 0
    character_results = []
    word_results = []
    while i < len(lines):
        l = lines[i]
        if "###" in l:
            print "\n%s" %l.split("###")[1]
        elif l.startswith("[1]"):
            category = l.split("[1]")[1]
            # skip next two lines (table header)
            i += 2
        else:
            l = l.split()
            if l[0].startswith("character"):
                formatted_line = "%s\t%s" % (category, "\t".join(l[1:]))
                character_results.append(formatted_line)
            elif l[0].startswith("word"):
                formatted_line = "%s\t%s" % (category, "\t".join(l[1:]))
                word_results.append(formatted_line)
            else:
                print "%s\t%s" %(category, "\t".join(l))
        i += 1

    print "results for character"
    for l in character_results:
        print l

    print "results for word"
    for l in word_results:
        print l


fname = sys.argv[1]
lines = read_file(fname)
format_output(lines)