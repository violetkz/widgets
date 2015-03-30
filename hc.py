#!/bin/env python
# -*- coding: utf-8 -*-

""" 
    the utilty to fix '#include' statament in C/CPP
"""
__version__ = '0.0.1'
__author__  = 'Kai Zhou'
__date__    = '2015-02-27 17:44:51'

import re,sys,os

def read_config(config_filename):
    try:
        gdict = {}
        execfile(config_filename, gdict)
        return gdict
    except Exception as e:
        print str(e)

class config_exception(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'Exception: ' + self.msg
        

LINE_NEED_FIX = True

class header_fixer:
    maker_pair = {'<':'>', '"':'"'}
    include_statament = re.compile(r'''^\s*\#\s*include\s+
            (?P<maker>[<"])\s*                  # char '<' or '"'
            (?P<filename>[\w_]+\.\w+)           # filename 
            \s*[>"]                             # char '>' or '"'
            ''',re.VERBOSE)
    header_filename = re.compile(r'[\w_]+\.(?:h)|(?:hpp)|(?:hxx)|(?:i)$', re.I)

    def __init__(self):
        self.line = ''
    
    def fix(self, line):
        m = self.include_statament.match(line)
        if m:
            fn = m.group('filename')
            flag, header = self.checkheader(fn)
            if flag:
                '''
                begin_maker = m.group('maker')
                new = '#include %s%s%s\n' % (begin_maker,
                           header,
                           self.maker_pair[begin_maker]
                          )
                '''
                new = line.replace(fn, header)
                return (flag, new)
        return (not LINE_NEED_FIX,line)
                
    
    def checkheader(self, header_filename):
        #raise 'Should implement check method'
        return (not LINE_NEED_FIX, header_filename)


class header_replace_fixer(header_fixer):
    def __init__(self, replace_rules = {}):
        header_fixer.__init__(self)
        self.rules = replace_rules

    def checkheader(self, header):
        if rules.has_key(header):
            return (LINE_NEED_FIX, self.rules[header])
        return (not LINE_NEED_FIX, header)

class header_relative_path_fixer(header_fixer):
    def __init__(self, basepaths = {}):
        header_fixer.__init__(self)
        self.headers = []
        self.__scan_header_files(basepaths)

    def __scan_header_files(self, basepaths):
        for bp in basepaths:
            for root, dirs, filenames in os.walk(bp):
                h_names = filter(
                        lambda x:
                            True if self.header_filename.match(x) else False,
                        filenames)
                if (not h_names): continue
                if bp != root:
                    relative_dir = root.partition(bp)[2].strip('./\/').replace('\\','/')
                    self.headers += map(lambda x:relative_dir + '/' + x,h_names)
                else:
                    self.headers += h_names
        #print self.headers

    def checkheader(self, header):
        optional_paths = []
        
        for h in self.headers:
            if header == h: return (not LINE_NEED_FIX, header)
            elif os.path.basename(h) == header:
                optional_paths.append(h);
            else: pass

        if optional_paths:
            if len(optional_paths) == 1:
                return (LINE_NEED_FIX, optional_paths[0])
            else:
                raise config_exception('duplicate optioanl paths %s.' % 
                        (optional_paths.join(':')))
        else:
            ## if not found, maybe it is standard libs, so skip it.
            return (not LINE_NEED_FIX, header)
    

#class filechecker:
class cpp_header_checker:
    cpp_filename = re.compile(r'[\w_]+\.(?:[ch])|(?:[ch]pp)|(?:[ch]xx)|(?:impl)|(?:i)$', re.I)
    def __init__(self, fixers = [], autosave = True, replace = False, suffix = '.hc', logger = sys.stdout):
        self.fixers = fixers
        self.replace= replace
        self.suffix = suffix
        self.autosave = autosave
        self.logger = logger

    def is_cpp_file(filename):
        if os.path.isfile(filename):
            return True if self.cpp_filename.match(os.path.basename(filename)) else False
        return False
    
    def _do_fix(self, line):
        l = line
        lf = False
        for f in self.fixers:
            nf,  l = f.fix(l)
            lf = lf | nf
        return (lf, l)

    def _save(self,filename, lines):
        nc = filename
        if not self.replace:
           nc = filename + self.suffix
        open(nc, 'w').writelines(lines)

    def check(self, filename):
        fixed_lines = []
        fixed_flag  = False
        with open(filename) as f:
            line_no = 0
            for line in f.readlines():
                line_no += 1
                f, nl = self._do_fix(line)
                if f: 
                    fixed_flag = f
                    fixed_lines.append(nl)
                    self.logger.write("[%s:%d] %s ==> %s\n" % (filename, line_no, 
                                line.strip('\r\n'), 
                                nl.strip('\r\n'))
                            )
                else: fixed_lines.append(line)
        if fixed_flag and self.autosave: 
            self._save(filename, fixed_lines)
        return (fixed_flag, fixed_lines)

def parse_option():
    import argparse
    parser = argparse.ArgumentParser(
            description='the script for fixing \'#include\' statament. ')
    g1 = parser.add_argument_group('options')
    g1.add_argument('-c','--configfile', action='store',
            default='hc.conf',
            help='config file name')
    g1.add_argument('-v', action='store_true', help='version')
    g1.add_argument('-p', '--report', action='store_true',
            default = False,
            help = 'change reporter')
    g1.add_argument('-w', '--replace', action='store_true',
            default = False,
            help = 'modify original file, no backup file')
    g1.add_argument('target', action='store', nargs='*', 
            help='src filename or directory')

    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = parse_option()
    if (args.v):
        print "verion: " + __version__
        sys.exit(0)
    report_fobj = open('report.txt', 'w') if args.report else sys.stdout
            
    config = read_config(args.configfile)
    rules = config['rules']
    basepaths = config['include_base_path']
    
    fixer = cpp_header_checker([
            header_replace_fixer(rules), 
            header_relative_path_fixer(basepaths)
            ], 
            logger = report_fobj,
            replace= args.replace)
    
    for p in args.target:
        if os.path.isfile(p): fiexer.check(p)
        elif os.path.isdir(p):
            for dir, _, files in os.walk(p):
                for f in files:
                    fixer.check(os.path.join(dir, f))
    sys.exit(0)
