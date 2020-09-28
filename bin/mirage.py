#!/usr/bin/python
import argparse
import glob
import os
import sys
import shutil
import json
import pickle


class MirageException(Exception):
    """ MirageException """
    pass


def load_config(path):
    with open(path, mode='r', encoding='utf_8') as f:
        return json.load(f)


def load_envdata(path):
    rtn = None
    try:
        with open(path, mode='rb') as f:
            rtn = pickle.load(f)
    except FileNotFoundError:
        rtn = None
    return rtn


def save_envdata(path, data):
    with open(path, mode='wb') as f:
        pickle.dump(data, f)
    return path


def setup_environemnt_data(confdata):
    envdata = {}
    for itm in confdata:
        envdata[itm['name']] = {'current': itm['initname']}
    return envdata


def extract_data(data, name):
    targetdata = list(filter(lambda x: x['name'] == name, data))
    if len(targetdata) == 0:
        return None
    else:
        return targetdata[0]


def cmd_namelist(data):
    for itm in data:
        print(itm['name'])


def cmd_show(data, names):
    for name in names:
        target = extract_data(data, name)
        if target is not None:
            print('name: {0}'.format(target['name']))
            print('path: {0}'.format(target['path']))
            print('backstage: {0}'.format(target['backstage']))
        else:
            print('{0} is not found in config file'.format(name), file=sys.stderr)


def swappathlst(prm):
    dirs = os.listdir(prm)
    dirs = [os.path.join(prm, f) for f in dirs if os.path.isdir(os.path.join(prm, f))]
    return dirs


def cmd_list(data, envdata, name):
    target = extract_data(data, name)
    print('current-> {0}'.format(envdata[name]['current']))
    if target is not None:
        dirs = swappathlst(target['backstage'])
        for d in dirs:
            print(os.path.basename(d))


def cmd_swap(data, envdata, name, to):
    target = extract_data(data, name)
    newenvdata = envdata
    if target is not None:
        dirs = swappathlst(target['backstage'])
        topath = list(filter(lambda x: os.path.basename(x) == to, dirs))
        if len(topath) == 0:
            raise MirageException('Target not found')
        else:
            topath = topath[0]
        path = target['path']
        if os.path.islink(path):
            os.remove(path)
            os.symlink(topath, path)
            newenvdata[name]['current'] = to
        else:
            print('[first run] creat link')
            shutil.move(path, target['backstage'] + os.sep + envdata[name]['current'])
            os.symlink(topath, path)
            newenvdata[name]['current'] = to
        return newenvdata
    else:
        raise MirageException('{0} not found'.format(name))


def cmd_current(envdata, name):
    print(envdata[name]['current'])


def cmd_new(data, name, newname):
    target = extract_data(data, name)
    if target is not None:
        backstage = target['backstage']
        path = backstage + os.sep + newname
        if os.path.exists(path):
            MirageException('{0} already exists')
        else:
            os.mkdir(path)
            print('mkdir -> ' + path)


def cmd_delete(data, name, delname):
    target = extract_data(data, name)
    if target is not None:
        backstage = target['backstage']
        path = backstage + os.sep + delname
        if os.path.exists(path):
            print('remove {0}'.format(path))
            confirm = input('OK? [type y/Y for YES] ')
            if confirm == 'y' or confirm == 'Y':
                shutil.rmtree(path)
                print('Removed')
            else:
                print('Abort')
        else:
            MirageException('{0} does not exist')


def run_cmd(data, envdata, cmdlst):
    cmd = cmdlst[0]
    newenvdata = envdata
    if cmd == 'namelist':
        cmd_namelist(data)
        return newenvdata
    elif cmd == 'show':
        cmd_show(data, cmdlst[1:])
        return newenvdata
    elif cmd == 'list':
        if len(cmdlst) >= 2:
            cmd_list(data, envdata, cmdlst[1])
            return newenvdata
        else:
            raise MirageException('Too few arguments')
    elif cmd == 'current':
        if len(cmdlst) >= 2:
            cmd_current(envdata, cmdlst[1])
            return newenvdata
        else:
            raise MirageException('Too few arguments')
    elif cmd == 'swap':
        if len(cmdlst) >= 3:
            newenvdata = cmd_swap(data, envdata, cmdlst[1], cmdlst[2])
            return newenvdata
        else:
            raise MirageException('Too few arguments')
    elif cmd == 'new':
        if len(cmdlst) >= 3:
            cmd_new(data, cmdlst[1], cmdlst[2])
            return newenvdata
        else:
            raise MirageException('Too few arguments')
    elif cmd == 'delete':
        if len(cmdlst) >= 3:
            cmd_delete(data, cmdlst[1], cmdlst[2])
            return newenvdata
        else:
            raise MirageException('Too few arguments')
    else:
        raise MirageException('Command not found')


def main(confpath, envpath, cmdlst):
    confdata = load_config(confpath)
    envdata = load_envdata(envpath)
    if envdata is None:
        envdata = setup_environemnt_data(confdata)
        save_envdata(envpath, envdata)
    if len(cmdlst) > 0:
        envdata = run_cmd(confdata, envdata, cmdlst)
        if envdata is not None:
            save_envdata(envpath, envdata)
    else:
        raise MirageException('Command not specified')


if __name__ == '__main__':
    # envdata path
    env_data_path = os.path.expanduser('~') + os.sep + '.miragedata.bin'
    # Default Path of onfigration file 
    default_conf_path = os.path.expanduser('~') + os.sep + '.mirageconf.json'
    # settting of argument parser
    parser = argparse.ArgumentParser(description='Swap directory script.')
    parser.add_argument('command', nargs='+', help='command and options')
    parser.add_argument('--conf', default=default_conf_path, help='configuration file path')
    args = parser.parse_args()
    # call main
    try:
        main(args.conf, env_data_path, args.command)
    except MirageException as e:
        print(e, file=sys.stderr)
