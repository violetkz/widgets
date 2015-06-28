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
    def __init__(self, name, value, left_child = None, right_child = None):
        self.name  = name
        self.value = value
        self.left  = left_child
        self.right = right_child

    def is_left_node(self):
        return (self.left == None) and (self.right == None)
        
    def __str__(self):
        s = "name: %s, value: %s\n  left: %s \n right: %s \n" % (
                self.name,
                self.value,
                str(self.left) if self.left else "Null",
                str(self.right) if self.right else "Null"
                )
        return s
        

def build_hufuman_tree(freq_tbl):
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

    #print len(node_list)
    #print str(node_list[0])
    tree_root_node = node_list[0]
    return tree_root_node

class encoder:
    def __init__(self, freq_tbl, left_char = '0', right_char = '1'):
        self.hufuman_tree_root_node = build_hufuman_tree(freq_tbl)
        self.code_tbl = self.__generate_code_dict(
                self.hufuman_tree_root_node, left_char, right_char)

    def __generate_code_dict(self, hufuman_tree_root_node, left_node_char, ritht_node_char):
        hf_code_tbl = {}
        def make_code(node, hf_code = ''):
            if node.left:
                make_code(node.left, hf_code + left_node_char)

            if node.right: 
                make_code(node.right, hf_code + ritht_node_char)

            if node.is_left_node():
                hf_code_tbl[node.name] = hf_code
            
        make_code(hufuman_tree_root_node, left_node_char)
        items = hf_code_tbl.items()
        items.sort()
        pprint.pprint(items)
        return hf_code_tbl

    def encode(self, input_file_object, out_file_object):
        origin_content = input_file_object.read()
        for c in origin_content:
            out_file_object.write(self.code_tbl[c])

class decoder:
    def __init__(self, freq_tbl, left_char = '0', right_char = '1'):
        self.left_char = left_char
        self.right_char = right_char
        self.hufuman_tree_root_node = build_hufuman_tree(freq_tbl)

    def decode(self, input_file_object, out_file_object):
        coded_content = input_file_object.read()

        ## make a head node to make loop easier.
        head_node = node("root",0, self.hufuman_tree_root_node, None)
        curr_node = head_node
        l = 0
        while l < len(coded_content):
            curr_char = coded_content[l]
            l += 1
            if (curr_char == self.left_char):
                curr_node = curr_node.left 
            elif (curr_char == self.right_char):
                curr_node = curr_node.right
            else:
                sys.stderr.write('unknown code: %s \n' % (curr_node))
                break

            if not curr_node: 
                sys.stderr.write('incorrect code\n')
                break
            elif curr_node.is_left_node():
                out_file_object.write(curr_node.name)
                curr_node = head_node

def encode_test(filename):
    #Test
    encoder_0_1 = encoder(freq_tbl)
    with open(filename,'rb') as f:
        with open('fun.c--','wb') as w:
            encoder_0_1.encode(f,w)

def decode_test(filename):
    decode_0_1 = decoder(freq_tbl)
    with open(filename,'r') as f:
        with open('fun.c~~','wb') as w:
            decode_0_1.decode(f,w)

if __name__=="__main__":
    encode_test("") 
    decode_test("") 
