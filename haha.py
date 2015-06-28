import sys,os
import fnmatch
import cPickle
import pprint

'''
def scan_char_frequency(sample_dir):
    count_tbl = {}
    char_sum  = 0.0
    
    for root, dirs, files in os.walk(sample_dir):
        for cfile in [c for c in files if fnmatch.fnmatch(c, "*.c")]:
            with  open(os.path.join(root,cfile), 'rb') as f:
                for line in f.readlines():
                    char_sum += len(line)
                    for c in line:
                        if count_tbl.has_key(c):
                            count_tbl[c] += 1;
                        else:
                            count_tbl[c] = 1;

    print "--char_sum: " + str(char_sum)
    char_frequency = [(char, round(char_count/char_sum * 100, 3)) for char, char_count in count_tbl.items()]
    print "--size: " + str(len(char_frequency))

    return char_frequency

freq_tbl = scan_char_frequency(os.path.expanduser("~/08_libs/linux/"))
freq_tbl.sort()
pprint.pprint(freq_tbl)
'''

freq_tbl = [
 ('\t', 3.538), ('\n', 3.855), (' ', 14.686), ('!', 0.157), ('"', 0.383), ('#', 0.205),
 ('$', 0.003), ('%', 0.128), ('&', 0.279), ("'", 0.098), ('(', 1.571), (')', 1.572),
 ('*', 1.267), ('+', 0.245), (',', 1.061), ('-', 1.027), ('.', 0.571), ('/', 0.705),
 ('0', 0.953), ('1', 0.395), ('2', 0.257), ('3', 0.142), ('4', 0.105), ('5', 0.091),
 ('6', 0.09), ('7', 0.052), ('8', 0.105), ('9', 0.073), (':', 0.19), (';', 1.524),
 ('<', 0.172), ('=', 1.152), ('>', 0.764), ('?', 0.024), ('@', 0.01), ('A', 0.467),
 ('B', 0.19), ('C', 0.459), ('D', 0.403), ('E', 0.778), ('F', 0.243), ('G', 0.169),
 ('H', 0.088), ('I', 0.569), ('J', 0.011), ('K', 0.087), ('L', 0.413), ('M', 0.279),
 ('N', 0.526), ('O', 0.432), ('P', 0.333), ('Q', 0.042), ('R', 0.574), ('S', 0.68),
 ('T', 0.621), ('U', 0.324), ('V', 0.081), ('W', 0.097), ('X', 0.105), ('Y', 0.073),
 ('Z', 0.037), ('[', 0.19), ('\\', 0.133), (']', 0.189), ('^', 0.004), ('_', 2.548),
 ('`', 0.003), ('a', 2.804), ('b', 1.098), ('c', 2.08), ('d', 2.691), ('e', 5.793),
 ('f', 1.774), ('g', 0.879), ('h', 1.185), ('i', 4.131), ('j', 0.045), ('k', 0.73),
 ('l', 1.906), ('m', 1.18), ('n', 3.656), ('o', 2.939), ('p', 1.434), ('q', 0.147),
 ('r', 3.688), ('s', 3.607), ('t', 4.62), ('u', 1.945), ('v', 0.655), ('w', 0.44),
 ('x', 0.53), ('y', 0.482), ('z', 0.133), ('{', 0.33), ('|', 0.158), ('}', 0.33),
 ('~', 0.013)]


class node:
    def __init__(self, name, value, left_child, right_child):
        self.name  = name
        self.value = value
        self.left  = left_child
        self.right = right_child
        
    def __str__(self):
        s = "name: %s, value: %s\n  left: %s \n right: %s \n" % (
                self.name,
                self.value,
                str(self.left) if self.left else "Null",
                str(self.right) if self.right else "Null"
                )
        return s
        

## convert k,v pair to node object
node_list = [node(name, value, None, None) for name, value in freq_tbl]

while len(node_list) > 1:
    ## sort by frequecy
    node_list.sort(key = lambda x : x.value) 
    left  = node_list[0]
    right = node_list[1]
    
    ## create new node 
    new_node = node(left.name + right.name, left.value + left.value, left, right)
    ## append new_node to node_list and remove left & right from node_list
    node_list.append(new_node)
    node_list.remove(left)
    node_list.remove(right)

#for a in  node_list:
#    print str(a)
print len(node_list)
print str(node_list[0])

hufuman_tree_root_node = node_list[0]

left_node_char  = '0'
ritht_node_char = '1'

hf_code = ''
hf_code_tbl = {}
def make_code(node, hf_code = ''):
    if node.left:
        hf_code += left_node_char
        make_code(node.left, hf_code)

    if node.right: 
        hf_code += ritht_node_char
        make_code(node.right, hf_code)

    if (not node.left) and (not node.right):
        hf_code_tbl[node.name] = hf_code
        

make_code(hufuman_tree_root_node, '0')
print hf_code_tbl

#Test
with open('udev.c','rb') as f:
    #data = f.read()
    with open('fun.c--','wb') as w:
        for line in f.readlines():
            for a in line:
                w.write(hf_code_tbl[a])
            w.write('\n')
