# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.

# __author__ =  Ken
# __email__  =  violet.kz@gmail.com
 
import os
import sys
import shlex

class info:
    def __str__(self):
        output = ''
        for k,v in self.__dict__.items():
           output += "\t%s = %s\n" % (k,v)
        return output

class BadConfException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
        
class simpleconfig:
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
        self.config   = info() 
        
    def _ITEM(self):
        key = self.lex.get_token()
        print key
        if key:
            sep = self.lex.get_token()
            print sep
            if not sep in [ ':', '=' ]:
                raise BadConfException( '`%s` is bad Sep Char.'% sep)
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
                raise BadConfException('except a \',\' or \']\' or \'{\', not: ' + c) 
        return array
        
    def parse(self):
        while True:
            key, value = self._ITEM()
            if key:
                setattr(self.config, key, value)
            else:
                break
        return self.config

if __name__== "__main__":
    info = simpleconfig(r'simpleconf.conf').parse()
    print info
    
