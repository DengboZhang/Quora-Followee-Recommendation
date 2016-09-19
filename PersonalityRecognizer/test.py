import subprocess
import shlex
import re

def run_command(cmd):
    cmd = shlex.split(cmd)
    return subprocess.check_output(cmd).decode('ascii')

'''
quesDirname = "/home/saurabh/IR_Project/user_ques_Xt/"

output = run_command('./PersonalityRecognizer -i ' + quesDirname + ' -d -t 2 -m 4')

    #output = run_command('./PersonalityRecognizer -i test.txt -t 2 -m 4')
    #print output

    scorefile = "/home/saurabh/IR_Project/scores_output"
    f = open(scorefile, 'w')
    f.write(output)
    f.close()
'''
scorefile = "/home/saurabh/IR_Project/scores_output"
f = open(scorefile, 'r')
data = []
lineList = []
with open(scorefile) as f:
    for line in f:
        if re.match(r'^\d*.txt', line):
            #print line
            lineList = line.split()
            print lineList


'''
if re.match(r'^*.txt', line):
            print line

    '''