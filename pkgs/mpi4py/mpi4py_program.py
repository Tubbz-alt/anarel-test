import sys
from mpi4py import MPI
import numpy as np
import time
import math
import argparse

comm = MPI.COMM_WORLD
rank = comm.rank
worldsize = comm.size
rank2host={}

def printOut(msg,rnk0=True):
        if rnk0 and not (rank==0):
                return
        hostmsg=''
        if len(rank2host)>0:
                hostmsg='%s: ' % rank2host[rank]
        sys.stdout.write("%srnk=%4d: %s\n" % (hostmsg, rank, msg))
        sys.stdout.flush()

def doBarrier(comm, rank, worldsize, rank2host=None):
        t0 = time.time()
        comm.Barrier()
        dt = time.time()-t0
        myDt=np.zeros(1, dtype=np.float32)
        allDt=np.zeros(worldsize, dtype=np.float32)
        myDt[0]=dt
        comm.Gather(sendbuf=[myDt, 1, MPI.FLOAT],
                    recvbuf=[allDt, MPI.FLOAT],
                    root=0)
        if rank==0:
                rankWaitingLongest = np.argmax(allDt)
                longestTime=allDt[rankWaitingLongest]
                hostmsg=''
                if (rank2host is not None) and len(rank2host)>0:
                        hostmsg = " host=%s" % rank2host[rankWaitingLongest]
                printOut("After MPI_Barrier. longest wait time: %.2f sec, rank=%d%s" % (longestTime,rankWaitingLongest, hostmsg))

def fillRank2host(comm, rank, worldsize, rank2host):
	hostname = MPI.Get_processor_name()
        allHostnames = comm.gather(hostname, root=0)
        if rank==0:
                for rankIdx, hostname in enumerate(allHostnames):
                        rank2host[rankIdx] = hostname

def checkCountsOffsets(counts, offsets, n):    
    '''Makes sure that the counts and offsets partition n. 
    
    Throws an exception if there is a problem

    Examples:
      >>> checkCountsOffsets(counts=[2,2,2], offsets=[0,2,4], n=6)
      # this is correct. 
      >>> checkCountsOffsets(counts=[2,2,2], offsets=[0,2,4], n=7)
      # incorrect, throws assert
      >>> checkCountsOffsets(counts=[2,2,2], offsets=[2,4,6], n=6)
      # incorrect, ect
    '''
    assert sum(counts)==n, 'counts=%r offsets=%r do not partition n=%d' % (counts, offsets, n)
    assert offsets[0]==0, 'counts=%r offsets=%r do not partition n=%d' % (counts, offsets, n)
    assert len(counts)==len(offsets), 'counts=%r offsets=%r do not partition n=%d' % (counts, offsets, n)
    for i in range(1,len(counts)):
        assert offsets[i]==offsets[i-1]+counts[i-1], 'counts=%r offsets=%r do not partition n=%d' % (counts, offsets, n)
    assert offsets[-1]+counts[-1]==n, 'counts=%r offsets=%r do not partition n=%d' % (counts, offsets, n)

def divideAmongWorkers(dataLength, numWorkers):
    '''partition the amount of data as evenly as possible among the given number of workers.

    Examples: 
      >>> divideAmongWorkers(11,3) 
      returns offsets=[0,4,8]
              counts=[4,4,3]    
    '''
    assert numWorkers > 0
    assert dataLength > 0
    k = int(math.floor(dataLength / numWorkers))
    r = dataLength % numWorkers
    offsets=[]
    counts=[]
    nextOffset = 0
    for w in range(numWorkers):
        offsets.append(nextOffset)
        count = k
        if r > 0: 
            count += 1
            r -= 1
        counts.append(count)
        nextOffset += count
    checkCountsOffsets(counts, offsets, dataLength)
    return offsets, counts            

def scatterDetector(comm, rank, worldsize, rank2host, numEvents, det, dtype, barrierBefore=True, barrierAfter=True, withCopy=False):
        dtype2mpiType = {np.float32:MPI.FLOAT, np.float64:MPI.DOUBLE, np.int16:MPI.INT16_T}
        dtype2bytes = {np.float32:4, np.float64:8, np.int16:2}
        assert dtype in dtype2mpiType, "unsupported dtype=%s" % dtype
        mpiType = dtype2mpiType[dtype]
        bytesPerElem = dtype2bytes[dtype]
        if det == 'cspad2x2':
            numElements=2*188*385
            detShape = (2,188,385)
        elif det == 'cspad':
            numElements = 32*188*385
            detShape = (32,188,385)
        else:
            raise Exception("unknown value for 'det' arg=%s" % det)
        bytesPerEvent = bytesPerElem*numElements
        mbAllEvents = bytesPerEvent*numEvents/float(1<<20)
        np.random.seed(153)
        detector = 100*np.random.random(detShape)
        detector = detector.astype(dtype)
        detector1dview = detector.reshape(numElements)
        mask = np.ones(detShape,dtype=np.bool)
        offsets, counts = divideAmongWorkers(numElements, worldsize-1)
        recvBuffer=np.zeros(0,dtype=dtype)
        sendBuffer=None
        if rank==0:
                if withCopy:
                        sendBuffer = np.empty(numElements, dtype=dtype)
                else:
                        sendBuffer = detector1dview
        else:
                recvBuffer = np.zeros(counts[rank-1], dtype=dtype)
        counts.insert(0,0)
        offsets.insert(0,0)
        counts = tuple(counts)
        offsets=tuple(offsets)
        t0 = time.time()
        for idx in range(numEvents):
                if barrierBefore:
                        comm.Barrier()
                if rank==0 and withCopy:
                        sendBuffer[:]=detector[mask]
                
                comm.Scatterv([sendBuffer, counts, offsets, mpiType],
                              recvBuffer,
                              root=0)
                if rank != 0:
                        assert recvBuffer[0] == detector1dview[offsets[rank]]
                if barrierAfter:
                        comm.Barrier()
        dt=time.time() - t0
        hz = float(numEvents)/dt
        mbsec = mbAllEvents/dt
        printOut("Scatterv: %s of %d events of %2d byte elements. Rate=%6.1f Hz at %6.1f MB/sec. Barriers: before=%r after=%r withCopy=%r" % \
                 (det, numEvents, bytesPerElem, hz, mbsec, barrierBefore, barrierAfter, withCopy))
        

if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('-n','--numevents',type=int,help='number of events to scatter',default=120)
        parser.add_argument('--cspad', action='store_true',help='scatter a full cspad sized amount of data')
        args = parser.parse_args()
        det = 'cspad2x2'
        if args.cspad:
                det = 'cspad'
        printOut("MPI Test. Before Initial MPI_Barrier. If no output follows, there is a problem with the cluster")
        printOut("worldsize=%d" % worldsize)
        doBarrier(comm,rank,worldsize)
        fillRank2host(comm,rank,worldsize,rank2host)
        comm.Barrier()
        printOut("MPI Test. Third MPI_Barrier, after synchronization and getting hostnames.")
        doBarrier(comm,rank,worldsize,rank2host)
        scatterDetector(comm, rank, worldsize, rank2host, numEvents=args.numevents, 
                        det=det, dtype=np.float32, barrierBefore=False, 
                        barrierAfter=True, withCopy=False)
