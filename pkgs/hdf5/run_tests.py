from __future__ import print_function

import sys
import os
import time
import tempfile
import atexit
import shutil


def run_command(cmd):
    print(cmd)
    assert 0==os.system(cmd), "cmd=%s failed" % cmd

def test_hdf5(outputdir):
    src = 'h5_cmprss.c'
    obj = os.path.join(outputdir, 'h5_cmprss.o')
    exe = os.path.join(outputdir, 'h5_cmprss')
    h5out = os.path.join(outputdir, 'cmprss.h5')
    cmd = 'h5c++ -c -o %s %s' % (obj, src)
    run_command(cmd)
    cmd = 'h5c++ -o %s %s' % (exe, obj)
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd
    cwd = os.getcwd()
    os.chdir(outputdir)
    run_command(exe)
    time.sleep(1)
    assert os.path.exists(h5out)
    os.chdir(cwd)

def test_parallel_hdf5(outputdir):
    src = 'Sample_mpio.c'
    obj = os.path.join(outputdir, 'Sample_mpio.o')
    exe = os.path.join(outputdir, 'Sample_mpio')

    cmd = 'h5pcc -c -o %s %s' % (obj, src)
    run_command(cmd)

    cmd = 'h5pcc -o %s %s' % (exe, obj)
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd

    cwd = os.getcwd()
    os.chdir(outputdir)
    cmd = 'mpirun -n 3 %s' % exe
    run_command(cmd)
    os.chdir(cwd)

def rmdir(dirname):
    shutil.rmtree(dirname)

if __name__ == '__main__':
    outputdir = tempfile.mkdtemp(prefix='test_conda_hdf5_')
    assert os.path.exists(outputdir), "tempfile.mkdtemp failed? dir=%s doesn't exist" % outputdir
    atexit.register(rmdir, outputdir)
    os.chdir(os.path.split(__file__)[0])
    test_hdf5(outputdir)
    test_parallel_hdf5(outputdir)
