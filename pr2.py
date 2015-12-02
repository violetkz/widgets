#!/bin/python
import os,sys,re
import subprocess
import cStringIO
import threading
op = os.path

class Pr2Exception(Exception):
    def __init__(self, what):
        self.what = what
    def __str__(self):
        return self.what

def my_check_call(args):
    returncode  = 0 
    try:
        if isinstance(args, list) or isinstance(args, tuple):
            subprocess.check_call(args)
        elif isinstance(args, str):
            subprocess.check_call(args, shell= True)
        else:
            raise Pr2Exception("Bad Type for function my_check_call")
    except subprocess.CalledProcessError as e:
        print  'run cmd: %s failed. returncode: %d' % (
                e.cmd, 
                e.returncode
                )
        returncode = e.returncode
    except Exception as e:
        print 'run cmd failed. ' + str(e)
        returncode = 0x0F
    finally:
        return returncode

# the wrapper of subprocess.Popen. if the type of args is string, call 
# subprocess.Popen with shell model. and if type of args is list or tuple,
# call subprocess.Popen with disable shell.
#
# >> simple_call(['grep', 'call', "p2.py"])
# >> simple_call("grep call p2.py);
#
def simple_call(*args):
    return my_check_call(args)

## run external program with shell.
#
# >> shcall(['ls', '-l'])
# >> shcall("ls -l")
#
def shcall(cmd):
    if isinstance(cmd, list) or isinstance(cmd, tuple):
        cmdstr = ' '.join(cmd)
    else:
        cmdstr = cmd
    return my_check_call(cmdstr)

class strfilter_exec_unit(threading.Thread):
    def __init__(self, func, input_file_obj, read_line = False):
        threading.Thread.__init__(self)

        self.input_file_obj = input_file_obj
        self.func = func
        self.read_line = read_line

        r,w = os.pipe()
        self.pw = os.fdopen(w, 'w')
        self.pr = os.fdopen(r, 'r')

    def output_pipe(self):
        return self.pr

    def run(self):
        while True:
            if self.read_line: 
                c = self.input_file_obj.readline()
            else:
                c = self.input_file_obj.read(1024)

            if c:
                re = self.func(c) #fixme, how to handle write?
                self.pw.write(re)
            else:
                break
        self.pw.close()

    def close(self):
        self.pr.close()

class prog_exec_unit():
    def __init__(self,args,
            input_file_obj = None, stderr = None, shell = False):
        self.args = args
        self.input_file_obj = input_file_obj
        self.shell = shell
        self.stderr = stderr

    def start(self):
        self.pc = subprocess.Popen(self.args, 
                stdin = self.input_file_obj,  stdout = subprocess.PIPE,
                stderr = self.stderr, 
                shell = self.shell)

    def output_pipe(self):
        if self.pc:
            return self.pc.stdout
        else:
            return None

    def close(self):
        self.pc.wait() 

## call external programs like shell pipe.
# 
# >> pcall('cat p2.py').pipe('grep pcall').show()
#
# it support python callable object.
# def myfunc(s):
#     return s.upper()
# >> pcall('cat p2.py').pipe(myfunc).pipe('grep PCALL').show()
#
class pcall():
    def __init__(self, args):
        self.excutable_unit_list = []
        self.eu = self.__create_exec_unit(args)
        self.excutable_unit_list.append(self.eu)
        self.eu.start()

    def __create_exec_unit(self, args, input_pipe = None, shell = False):
        ## the type of args is function, excute 'strfilter_exec_unit'
        if hasattr(args, '__call__'):
            return strfilter_exec_unit(args, input_pipe)

        else:
            print type(args)
            ## the type of args is string, list or tuple, it be excute by external command.
            if shell:
            #  make a string to shell. 
                if isinstance(args, list) or isinstance(args, tuple):
                    args = ' '.join(args)
                elif isinstance(args, str):
                    pass
                else:
                    raise Pr2Exception("Bad type for 'pcall'. only string,list and"
                                        "tuple are supported.")
            else:
                # split to array if shell flag is false
                if  isinstance(args, str):
                    args = shlex.split(args)
                elif isinstance(args, list) or isinstance(args, tuple):
                else:
                    raise Pr2Exception("Bad type for 'pcall'. only string,list and"
                                        " tuple are supported.")

            return prog_exec_unit(args, input_pipe, stderr = None, shell = shell)

    def pipe(self, args):
        eu = self.__create_exec_unit(args, input_pipe = self.eu.output_pipe())
        self.excutable_unit_list.append(eu)
        self.eu = eu
        self.eu.start()

        return self

    def show(self):
        buff = cStringIO.StringIO()
        while True:
            c = self.eu.output_pipe().read(1024)
            if c: buff.write(c)
            else: break
        self.close()
        return buff.getvalue()

    def close(self):
        for eu in self.excutable_unit_list:
            eu.close()

if __name__=="__main__":
    def test(x):
        return x.upper()
    print pcall(['cat', 'a.log']).pipe(['grep', 'accept']).pipe(test).show()
    print pcall(['cat', 'a.log']).pipe(['grep', 'accept']).pipe(test).show()
    

