from __future__ import print_function

import sys
import os
import time
import numpy as np
import tempfile
import atexit
import shutil
import mpi4py
from mpi4py import MPI
import h5py

def test_h5py(outputdir):
    fname = os.path.join(outputdir, 'run_test_helloworld.h5')
    f = h5py.File(fname,'w')
    f['data'] = 'hello world!'
    f['data2'] = np.zeros((3,5), np.int32)
    del f
    h5 = h5py.File(fname,'r')
    assert h5['data'].value == 'hello world!'
    assert h5['data2'].shape[0]==3
    assert h5['data2'].shape[1]==5
    assert np.sum(h5['data2'][:])==0

    sys.stdout.write("mpi version: %r\n" % (MPI.get_vendor(),))
    return 0

def rmdir(dirname):
    shutil.rmtree(dirname)

if __name__ == '__main__':
    outputdir = tempfile.mkdtemp(prefix='test_conda_openmpi_')
    assert os.path.exists(outputdir), "tempfile.mkdtemp failed? dir=%s doesn't exist" % outputdir
    atexit.register(rmdir, outputdir)
    os.chdir(os.path.split(__file__)[0])
    sys.exit(test_h5py(outputdir))
