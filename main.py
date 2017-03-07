#!/usr/bin/python
import imp
import os
import subprocess
import os.path
import sys
import shlex
import string
import traceback
import getopt, sys
from threading import Thread

__usage__ = '''Usage:
./main.py KEY
    -f, --file=FILE  set path of file with settings
Examples: 
./main.py -f config.py
./main.py --file=config.py
'''

def load_settings():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        print __usage__
        sys.exit(2)
    input = None
    if not opts:
        print __usage__
        sys.exit(0)
    o, a = opts[0]
    if o in ("-h", "--help"):
        print "HELP:"
        print __usage__
        sys.exit(0)
    if o in ("-f", "--file"):
        input = a
    else:
        assert False, __usage__
    try:
        settings = imp.load_source('settings', input)
    except:
        print sys.exc_info()
        print __usage__
        sys.exit(2)
    try:
        os.unlink(input + 'c')
    except:
        pass
    try:
        os.unlink(input + 'o')
    except:
        pass    
    return [(settings.COMMAND + ' ' + f + ' ' + settings.ARGS, f, settings.FILTER) for f in settings.FILES]
        

class MyThread(Thread):
    def __init__(self, command, file_name, filt):
        super(MyThread, self).__init__()
        self.command = command
        self.filt = filt
        self.file_name = file_name
        self.daemon = True
        self.start()
    
    def getOutput(self):
        return (self.file_name, self.filt(self.file_name, self.output))

    def run(self):
        args = shlex.split(self.command)
        #print args
        self.p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.output, err = self.p.communicate()
        while (self.p.poll() is None):
            continue
        #print p.stdout.readlines()
       # print err
        

def check_thread(thread):
    res = thread.is_alive()
    if res:
        return True
    thread.join()
    o = thread.getOutput()
    #global outputNum
    #print str(outputNum) + ') ' + os.path.split(o[0])[1] + ':'
    print o[1]# + '\n'
    #outputNum += 1
    return False

def main():
    sets = load_settings()
    #for par in sets:
    #    print par
    #quit()
    monitor = [MyThread(par[0].encode("utf8"), par[1].encode("utf8"), par[2]) for par in sets]   
    while monitor:
        monitor[:] = [i for i in monitor if check_thread(i)]
        
if __name__ == '__main__':
    main()
