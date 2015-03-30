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
    
    

