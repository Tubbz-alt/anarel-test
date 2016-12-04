from __future__ import print_function

import sys
import os
import tempfile
import atexit
import shutil

def run_command(cmd):
    print(cmd)
    assert 0 == os.system(cmd), "cmd failed: %s" % cmd

def test_mpi(outputdir):
    exe = '%s/communicator_mpi' % outputdir
    cmd = 'mpicc -o %s/communicator_mpi communicator_mpi.c' % outputdir
    run_command(cmd)
    assert os.path.exists(exe), "%s failed" % cmd

    cmd = 'mpirun -n 3 %s' % exe
    run_command(cmd)

def rmdir(dirname):
    shutil.rmtree(dirname)

if __name__ == '__main__':
    outputdir = tempfile.mkdtemp(prefix='test_conda_openmpi_')
    assert os.path.exists(outputdir), "tempfile.mkdtemp failed? dir=%s doesn't exist" % outputdir
    atexit.register(rmdir, outputdir)
    os.chdir(os.path.split(__file__)[0])
    test_mpi(outputdir)
