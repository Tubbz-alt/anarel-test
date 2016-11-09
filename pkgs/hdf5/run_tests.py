from __future__ import print_function

import sys
import os
import time

def run_command(cmd):
    print(cmd)
    os.system(cmd)

def test_hdf5():
    src = 'h5_cmprss.c'
    exe = 'h5_cmprss'
    h5out = 'cmprss.h5'

    if os.path.exists(exe):  os.unlink(exe)
    if os.path.exists(h5out):  os.unlink(h5out)
    cmd = 'h5c++ -o %s %s' % (exe, src)
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd

    cmd = './%s' % exe
    run_command(cmd)
    time.sleep(1)
    assert os.path.exists(h5out)
    os.unlink(h5out)
    os.unlink(exe)

def test_parallel_hdf5():
    src = 'Sample_mpio.c'
    exe = 'Sample_mpio'
    if os.path.exists(exe):  os.unlink(exe)

    cmd = 'h5pcc -o %s %s' % (exe, src)
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd

    cmd = 'mpirun -n 3 ./%s' % exe
    run_command(cmd)
    os.unlink(exe)

if __name__ == '__main__':
    os.chdir(os.path.split(__file__)[0])
    test_hdf5()
    test_parallel_hdf5()
