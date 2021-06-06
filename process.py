from subprocess import Popen, PIPE

def runNONMEM:
    process = Popen(['echo', 'test.py'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print stdout