import os
import sys
import shlex

class TaskInfo:
    def __str__(self):
        output = ''
        for k,v in self.__dict__.items():
           output += "\t%s = [%s]\n" % (k,v)
        return output

class BadConfException:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
        
class Config:
    '''
    SYNTAX:
        FILE      :=    ITEMS
        ITEMS     :=    ITEM | ITEMS
        ITEM      :=    KEY Separator VALUE
        Separator :=    ':'  | '='
        VALUE     :=    WORD | ARRAY
        ARRAY     :=    '[' LIST ']' | '{' LIST '}'
        LIST      :=    WORD |  WORD ',' LIST
    '''
    def __init__(self, filename):
        self.f   = open(filename)
        self.lex = shlex.shlex(self.f, posix=False)
        
    def _ITEM(self):
        key = self.lex.get_token()
        if key:
            sep = self.lex.get_token()
            if not sep in [ ':', '=' ]:
                raise BadConfException('%s: Bad Sep Char.'%
                        self.lex.error_leader())
            value = self._VALUE()
            return (key, value)
        else:
            return (None, None)

    def _VALUE(self):
        c = self.lex.get_token()
        if c in ['[', '{']:
            return self._ARRAY()
        else:
            return self._WORD(c)

    def _WORD(self, c):
        if c == "None" or c == '""' :
            return '' 
        else:
            return c.strip('"')

    def _ARRAY(self):
        array = []
        c = self.lex.get_token()
        while not c in [']', '}']:
            array.append(self._WORD(c))
            c = self.lex.get_token()
            if c in [']', '}']:
                break
            elif c == ',':
                c = self.lex.get_token()
            else:
                raise BadConfException('%s: except a \',\' or \']\' or \'{\'',
                        self.lex.error_leader()) 
        return array
        
    def parse(self):
        info = TaskInfo();
        while True:
            key, value = self._ITEM()
            if key:
                setattr(info, key, value)
            else:
                break

if __name__== "__main__":
    info = Config(r'simpleconf.py').parse()
    print info
    
