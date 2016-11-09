from __future__ import print_function

import sys
import os
import time

def run_command(cmd):
    print(cmd)
    return os.system(cmd)

def test_mpi4py():
    assert 0==run_command('mpirun -n 3 python mpi4py_program.py')
    return 0

if __name__ == '__main__':
    os.chdir(os.path.split(__file__)[0])
    sys.exit(test_mpi4py())
