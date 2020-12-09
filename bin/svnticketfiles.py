#!/bin/python

import sys
import subprocess
import re


def get_svnlog(id):
    svncmd = 'svn log --search #{}'.format(id)
    return subprocess.run(svncmd.split(' '), encoding='utf-8', stdout=subprocess.PIPE).stdout


def parselog_1(lst, rtn):
    if len(lst) < 1:
        return rtn
    else:
        fst = lst[0]
        head_m = re.match(r'^---+$', fst)
        if head_m:
            if len(lst) < 2:
                return rtn
            else:
                header = lst[1]
                rev = header.split(' ')[0]
                return parselog_1(lst[2:], rtn + [rev])
        else:
            return parselog_1(lst[1:], rtn)
                    

def parselog(str):
    liststr = str.split("\n")
    liststr = liststr[0:-1]
    return parselog_1(liststr, [])


def parsediffsummarize_1(line):
    splitline = line.split(' ')
    return {'type': splitline[0], 'name': splitline[-1]}


def parsediffsummarize(str):
    lst = str.split('\n')[0:-1]
    return map(parsediffsummarize_1, lst)
    

def get_diff_files(rev):
    cmd = 'svn diff -r r{}:PREV --summarize'.format(rev)
    cmdresult = subprocess.run(cmd.split(' '), encoding='utf-8', stdout=subprocess.PIPE).stdout
    return {'rev': rev, 'files': parsediffsummarize(cmdresult)}

    
def get_relatefiles(revs):
    return map(get_diff_files, revs)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Specify the ticket ID', file=sys.stderr)
        sys.exit(1)
    else:
        # get related svn log
        logtxt = get_svnlog(sys.argv[1])
        # parse log message and get rev numbers
        revs = parselog(logtxt)
        # get related files of parsed rev
        result = get_relatefiles(revs)
        # show result
        for rev in result:
            print('rev:{}'.format(rev['rev']))
            for f in rev['files']:
                print('{}, {}'.format(f['type'], f['name']))
    