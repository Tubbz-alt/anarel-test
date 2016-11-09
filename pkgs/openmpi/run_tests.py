from __future__ import print_function

import sys
import os
import subprocess as sb

def run_command(cmd):
    print(cmd)
    os.system(cmd)

def test_mpi():
    exe = 'build/communicator_mpi'
    if os.path.exists(exe):  os.unlink(exe)
    cmd = 'mpicc -o build/communicator_mpi communicator_mpi.c'
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd

    cmd = 'mpirun -n 3 %s' % exe
    run_command(cmd)

if __name__ == '__main__':
    os.chdir(os.path.split(__file__)[0])
    test_mpi()
