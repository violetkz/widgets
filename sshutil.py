#!/bin/env python2
# -*- coding: utf-8 -*-

""" 
    A utility class for ssh operation.  
"""
__version__ = '1.0.0'
__author__  = 'Ken'
__date__    = '2017-05-04 21:42:28'

import os,sys
import subprocess
import shlex
import logging
import StringIO
import json
import signal
op = os.path

debug_mode = False

def debug(*args):
    if debug_mode: print '->' + ' '.join(args)
def info(*args):  print '--' + ' '.join(args)
def error(*args): print '~~' + ' '.join(args)

class SSHOptException(Exception):
    def __init__(self, errmsg):
        self.msg = errmsg
    def __str__(self):
        return 'SSHOptException: ' + self.msg


class SSHOpt:
    ''' The wrapper of SSH command for remote host operations '''
    def __init__(self, host, **kwargs):

        self.host = host
        self.user = kwargs.get('user')
        self.passwd = kwargs.get('passwd') ## unused.
        self.keyfile = kwargs.get('key')
        
        if self.user:
            self.login_info = "%s@%s" % (self.user, self.host)
        else:
            self.login_info = host


    def _exec(self, cmd, out = None, readline = False, timeout = None, **kwargs):

        if isinstance(cmd, str) or isinstance(cmd, unicode):
            debug(cmd)
            exe_args = shlex.split(str(cmd))
        elif isinstance(cmd, list):
            debug(' '.join(cmd))
            exe_args = cmd
        else:
            debug(cmd)
            raise SSHOptException('bad exe args type')

        p = subprocess.Popen(exe_args, stdin = None, stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT, **kwargs)

        
        timer = None
        process_states = 0x00  
        
        ## helper function to kill the process, when it timeout.
        def handle_timeout():
            p.terminate()
            process_states = 0xFE ## killed by signal

        if timeout:
            import threading
            timer = threading.Timer(timeout, handle_timeout)
            timer.start()

        if out:
            if not readline:
                output, unused = p.communicate()
                out.write(output)
            else:
                ## read output each line to avoid large output.
                while True:
                    d =  p.stdout.readline()
                    if not d: break
                    out.write(d)
        p.wait()

        if timer: timer.cancel()
            
        returncode  =  p.returncode if process_states == 0x00  else process_states
        return returncode

    def _check_out(self, cmd, shell = False):
        
        strio = StringIO.StringIO()
        rc = self._exec(cmd,strio, shell = False) 
        output = strio.getvalue()
        strio.close()
        return (rc, output)

    def _check_connect(self):
        rc = self._exec("ssh %s 'echo ${HOSTHOME} >/dev/null'" % self.login_info, timeout = 10)
        if rc == 0: return True
        return False
    
    def rsync(self, src, dest, identical = False, verbose = False, extra_sync_args=""):
        ''' sync files or directories with remote host
        '''

        if src.startswith('$-'): src = src.replace('$-', self.login_info)
        if dest.startswith('$-'):dest = dest.replace('$-', self.login_info)

        if src.startswith('~'): src = op.expanduser(src)
        # TODO: Need expand variable for local path, like  $HOME/$HOST
        if dest.startswith('~'): dest = op.expanduser(src)


        rsync_option = ['-az', '-e ssh']
        if verbose:          rsync_option.append('-v')
        if op.isdir(src): 
            rsync_option.append('-r')
            if identical: 
                rsync_option.append('--delete') 
        if extra_sync_args:
            rsync_option.append(extra_sync_args)
            
        # TODO: Need expand variable for local path?
        cmd = 'rsync %s "%s" "%s"' % (
                ' '.join(rsync_option),
                #op.expanduser(src),
                src,
                dest)
        return self._check_out(cmd)
    
    def rexec(self, cmd, cwd = '.', out = None, strict = True, timeout = None, **kwargs):
        ''' execute the command with arguments, wait for command to complete. 
        return the a couple of returncode and output.
        '''

        cmds =  ['ssh','-T', self.login_info]
        args = []

        if cwd != '.': args.append('cd ' + cwd)

        if isinstance(cmd, str) and cmd:
            args.append(cmd)
        elif isinstance(cmd, list):
            ## to avoild some error, execute the command with brackets
            #cmd = ["{%s;}"%x for x in cmd]
            args.extend(cmd)
        
        seq_char = ' && '
        if not strict: seq_char = ';'

        cmds.append(seq_char.join(args))
        if not out:
            return self._check_out(cmds)
        
        return (self._exec(cmds, out, readline = True, **kwargs), "")


EXEC_JOB_RC_OK      = 0
EXEC_JOB_RC_FAILED  = 1

def test():

    sshopt = SSHOpt('envtest', user = 'xmbuild')
    rc, l =  sshopt._check_out("ls -l")
    if rc == 0:
        print l
    else:
        print 'err' + l 

    print sshopt.rsync(r'./readme.html', r'$-:~/')
    print sshopt.rexec('ls -l', '/tmp')
    print sshopt.rexec(['ls -l', 'ls *.xml | wc -l '], '/tmp')
    print sshopt.rexec("echo \"$HOME\"")

def test_timeout():
    sshopt = SSHOpt('envtest', user = 'test')
    print sshopt._check_connect()



## $ ./xmjob sles10x86 src-dir action
## $ ./xmjob target-host <src-dir> <action>
#     if src-dir is not specified, try to read from configure file.
#     if action is not sepcified, by default, the tools will try
#     to execute 'complie.*' in the root or build directory of src-dir
#     in the remote target.
if __name__=="__main__":
    rhel_targets = ['tc_rhel5x86','tc_rhel5x64','tc_rhel6x86','tc_rhel6x64']
    sles_targets = ['tc_sles10x86','tc_sles10x64','tc_sles11x86','tc_sles11x64']

    all_targes = rhel_targets + sles_targets
    
    from multiprocessing import Pool
    
    #basicConfig(filename='myapp.log', level=logging.DEBUG)
    pool = Pool(len(all_targes))
    
    returncode = 1

    try:
        rc = pool.map(ice_build_job, all_targes) 
        if rc.count(EXEC_JOB_RC_OK) == len(rc): 
            returncode = 0

    except (KeyboardInterrupt, SystemExit):
        info('closing pool.')
        #Stops the worker processes immediately without completing outstanding
        #work. When the pool object is garbage collected terminate() will be
        #called immediately.
        pool.terminate()
        ## due to strange issue of std thread lib, here never come in. 
        ## refer to  thread lib doc on the official site.
        pool.join()

    except Exception as e:
        
        ## FIXME: the following code is just for debug mode. Should remove it
        ## under release mode.
        import traceback
        print '-' * 25
        traceback.print_exc()
        error(traceback.format_exc())
        print '-' * 25

    finally:
        #info('closing pool.')
        #Stops the worker processes immediately without completing outstanding
        #work. When the pool object is garbage collected terminate() will be
        #called immediately.
        #pool.terminate()
        info('closing pool.')
	pool.close()
        pool.join()
        
    sys.exit(returncode)
