#!/bin/python

import sys
import subprocess
import xml.etree.ElementTree as ET


# svn diff econding
encode_code = 'utf-8'


def get_svnlog(id):
    svncmd = 'svn log --search #{} --xml'.format(id)
    return subprocess.run(svncmd.split(' '), encoding='utf-8', stdout=subprocess.PIPE).stdout


def confirmation_id(logentry, id):
    msg = logentry.find('msg').text
    msg = msg.rstrip()
    msgfinalline = msg.split('\n')[-1]
    msgfinalline = msgfinalline.lstrip()
    revstr = msgfinalline.split(' ')[1]
    revnum = int(revstr.replace('#',''))
    if int(id) == revnum:
        return True
    else:
        return False
    

def parselog(xmlstr, id):
    rtn = []
    root = ET.fromstring(xmlstr)
    for logentry in root:
        if confirmation_id(logentry, id):
            rtn.append('r{}'.format(logentry.attrib['revision']))
    return rtn


def parsediffsummarize_1(line):
    splitline = line.split(' ')
    return {'type': splitline[0], 'name': splitline[-1]}


def parsediffsummarize(str):
    lst = str.split('\n')[0:-1]
    return map(parsediffsummarize_1, lst)


def minus_rev(rev):
    revnum = int(rev.replace('r', ''))
    return 'r{}'.format(revnum - 1)


def get_diff_files(rev):
    cmd = 'svn diff -r {}:{} --summarize'.format(minus_rev(rev), rev)
    cmdresult = subprocess.run(cmd.split(' '), encoding=encode_code, stdout=subprocess.PIPE).stdout
    return {'rev': rev, 'files': parsediffsummarize(cmdresult)}

    
def get_relatefiles(revs):
    return map(get_diff_files, revs)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Specify the ticket ID', file=sys.stderr)
        sys.exit(1)
    else:
        # get related svn log
        logxml = get_svnlog(sys.argv[1])
        # parse log message and get rev numbers
        revs = parselog(logxml, sys.argv[1])
        # get related files of parsed rev
        result = get_relatefiles(revs)
        # show result
        for rev in result:
            print('rev:{}'.format(rev['rev']))
            for f in rev['files']:
                print('{}, {}'.format(f['type'], f['name']))
    
