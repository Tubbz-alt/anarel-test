# it is important to make sure that
# conda works in the dev installations
# before we upgrade it in the prod
# installations.

from __future__ import print_function

import sys
import os
try:
    import urllib2
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError


import subprocess as sb

def run_command(cmd):
    print(cmd)
    return os.system(cmd)


def internet_on():
    # http://stackoverflow.com/questions/3764291/checking-network-connection
    try:
        response=urlopen('http://google.com',timeout=5)
        return True
    except URLError as err: pass
    return False

def create_new_env(name):
    # this will fail if environment not present, that's Ok.
    run_command('conda env remove -n %s -y -q' % name)
    return run_command('conda create -n %s -y -q numpy' % name)

def activate_new_env(name):
    assert 0 == run_command('''source activate %s && python -c "import numpy" && source deactivate''' % name)
    return 0

def clone_central_env(central_env, usr_env):
    # test clones an existing environment. First remove target if it exists.
    # Removing target command will fail if it doesn't exist, so we don't check
    # return code of next command
    run_command('conda env remove -n %s -y -q' % usr_env)

    # now clone
    cmds = ['conda create -n %s -y -q --clone %s' % (usr_env, central_env),
            '''source activate %s && python -c "import yaml" && source deactivate''' % usr_env]
    for cmd in cmds:
        retcode = run_command(cmd)
        assert retcode == 0, "cmd=%s returned %d" % retcode
    return 0

if __name__ == '__main__':
    if not internet_on():
        print("conda/run_tests.py: There appears to be no internet access from this host. Not doing tests.")
        sys.exit(0)
    assert 0 == create_new_env('testing_new_env')
    assert 0 == activate_new_env('testing_new_env')
    assert 0 == clone_central_env(central_env='manage', usr_env='test_clone_manage')

