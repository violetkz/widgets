widgets
=======

A collection of code/utilities which wrote by myself.

# simpleconfig.py 
it is a very simple config file parser

```python
#import simpleconfig

info = simpleconfig(r'simpleconf.conf').parse()
print info
```

# hc.py
it is a utility to to fix '#include' statament in C/CPP

```shell
$ ./hc.py --help
usage: hc.py [-h] [-c CONFIGFILE] [-v] [-p] [-w] [target [target ...]]

the script for fixing '#include' statament.

optional arguments:
  -h, --help            show this help message and exit

options:
  -c CONFIGFILE, --configfile CONFIGFILE
                        config file name
  -v                    version
  -p, --report          save report into file 'report.txt'
  -w, --replace         modify original file, no backup file
  target                src filename or directory
```
    
# haha.py
A funny script! it is able to encode your src code file with two specified 
different charaters. like below:

- encode file with '0' and '1'
    ``` shell
    $ echo '#include <stdio.h>\n int main() { puts("haha"); return 0; }' | python haha.py -c '01'  | tee fun.c
    ```
    the output:
    ```
    01001000000111110101100111101011100001110010010010011101100010001110010101000100
    01001011111001101000010000001100001100110111010110011111010110000100110000011100
    10110111110101100100010010001101100010001000110001010101110010001001010101000100
    01100101000110000101100011000010110011001010100011010000001100101110011100010011
    100101011101011001100101001101000000110001000101011101
    ```

    decode it! 
    ```
    $ cat fun.c | python haha.py -d -c '01' -o /tmp/t.c && gcc -o ./fun /tmp/t.c  && ./fun
    ```
    the output:
    ```
    haha
    ```
- encode file with whitespace and tab
    ``` shell
    $ echo '#include <stdio.h>\n int main() { puts("haha"); return 0; }' | python haha.py -c ' \t'  | tee fun.c
    ```
    all charaters is disappear in the output. :laughing::laughing::laughing:
    ```
                                                                                                                                                          


                                                                                                                                                          
                                                                                                                                                          
                                                                                                                                                          

    ```

    decode it! 
    ```
    $ cat fun.c | python haha.py -d -c ' \t' -o /tmp/t.c && gcc -o ./fun /tmp/t.c  && ./fun
    ```
    the output:
    ```
    haha
    ```


# pr2.py
A few wrapper functions of subprocess module to call external program.

- function: *simple_call*, *shcall*
```python
 # the simple wrapper of subprocess.Popen
 >> simple_call(['grep', 'call', "p2.py"])

 # run external program with shell.
 >> shcall(['ls', '-l'])
 >> shcall("ls -l")

 # call external programs like shell pipe.
 >> pcall('cat p2.py').pipe('grep pcall').show()

 # orit support python callable object.
 def myfunc(s):
     return s.upper()
 >> pcall('cat p2.py').pipe(myfunc).pipe('grep PCALL').show()
```
    

# sshutil.py
A utility class for ssh operation.  

- example.
```python
  # init a instance of ssh operation
  sshopt = SSHOpt('envtest', user = 'xmbuild')
  # sync local file './readme.html' to remote $HOME/, here the perfix '$-:' mean it is the
  # path of remote side.
  print sshopt.rsync(r'./readme.html', r'$-:~/')
  # exec a command on directory '/tmp' of remote side, and print the output.
  print sshopt.rexec('ls -l', '/tmp')
  # exec a set of commands on the directory of remote side , and print the output.
  print sshopt.rexec(['ls -l', 'ls *.xml | wc -l '], '/tmp')
```
