#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import subprocess as sb

'''produces list of all bins, imports, and libs in the
current python installation'''

############# python3 porting issues ##############
# http://python3porting.com/differences.html
if sys.version_info < (3,):
    def b(x):
        return x
else:
    import codecs
    def to_bytes(x):
        return codecs.latin_1_encode(x)[0]
############### python 3 porting #####################

######## Imports ###################
def isModuleFile(fullfname):
    if fullfname.endswith('.py') or fullfname.endswith('.so') and not fullfname.startswith('__'):
        return True
    return False

def isModulePackage(fullfname):
    initFile = os.path.join(fullfname, '__init__.py')
    if os.path.exists(initFile):
        return True
    return False

def lookForSubModules(imports, import_set, basedir, modList, verbose):
    if verbose: print("  === %s ===" % '.'.join(modList))
    for fname in os.listdir(basedir):
        fullfname = os.path.join(basedir, fname)
        if isModulePackage(fullfname):
            newImport = '.'.join(modList) + '.' + fname
            if newImport in import_set:
                sys.stderr.write("WARNING: import %s from %s masked, comin from directory earlier in sys.path" %
                                 (newImport, fullfname))
            else:
                imports.append(newImport)
                import_set.add(newImport)
            lookForSubModules(imports, import_set, fullfname, modList + [fname], verbose)
    
def lookForTopLevelModules(imports, import_set, basedir, verbose):
    for fname in os.listdir(basedir):
        fullfname = os.path.join(basedir, fname)
        if isModuleFile(fullfname): imports.append(os.path.splitext(fname)[0])
        elif isModulePackage(fullfname):
            if fname in import_set:
                sys.stderr.write("WARNING: import %s from %s is masked, must exist in directory earlier in sys.path" %
                                 (fname, fullfname))
            else:
                imports.append(fname)
                import_set.add(fname)
            lookForSubModules(imports, import_set, fullfname, [fname], verbose)
            
def getImports(verbose=False):
    imports = []
    import_set = set([])
    pythonPathOtherThanCurrentDirectory = sys.path[1:]
    for path in pythonPathOtherThanCurrentDirectory:
        if os.path.isdir(path):
            numberBefore = len(imports)
            lookForTopLevelModules(imports, import_set, path, verbose)
            if verbose: print("=== sys.path: %s === %d imports" % (path, len(imports)-numberBefore))
    return imports

############ bins #################
def getBins(verbose=False):
    bins = []
    pythonBin = sb.check_output('which python', shell=True, universal_newlines=True)
    binDir = str(os.path.split(pythonBin)[0])
    if verbose: print("getBins: looking for bins in %s" % binDir)
    for fname in os.listdir(binDir):
        fname = str(fname) # python 3, for some reason os.listdir not always a sting?
        if fname.startswith('.'): continue
        fullBin = os.path.join(binDir, fname)
        if os.path.isfile(fullBin) and os.access(fullBin, os.X_OK):
            bins.append(fname)
    if verbose: print("getBins: identified %d bins" % len(bins))
    bins.sort()

    # are any of these bins masked?
    for bin in bins:
        p = sb.Popen('which %s' % bin, shell=True, stdout=sb.PIPE, stderr=sb.PIPE, universal_newlines=True)
        out,err = p.communicate()
        assert err.strip()=='', "binTest: error running which %s, err=%s" % (bin, err)
        assert p.returncode==0, "error running which %s" % bin
        if os.path.abspath(out.strip()) != os.path.abspath(os.path.join(binDir, bin)):
            sys.stderr.write("WARNING: getBins:  the bin %s, which is in the same directory as python, is masked by another directory in the PATH" % bin)
    return bins

############ libs #################
def getLibs(verbose=False):
    libs = []
    pythonBin = sb.check_output('which python', shell=True, universal_newlines=True)
    binDir = os.path.split(pythonBin)[0]
    libDir = os.path.join(os.path.split(binDir)[0], 'lib')
    if not os.path.exists(libDir):
        print("ERROR: couldn't find libDir: %s" % libDir)
        return libs
    if verbose: print("getLibs: looking in %s" % libDir)
    for fname in os.listdir(libDir):
        if fname.startswith('.'): continue
        fullfname = os.path.join(libDir, fname)
        if os.path.isfile(fullfname) and os.path.splitext(fname)[1] == '.so':
            libs.append(fname)
    libs.sort()
    if verbose: print("getLibs: found %d libs" % len(libs))
    return libs


if __name__ == '__main__':
    print("=========== bins =============")
    bins = getBins(verbose=False)
    print('\n'.join(bins))

    print("\n\n=========== imports =============")
    imports = getImports(verbose=False)
    print('\n'.join(imports))

    print("\n\n=========== libs =============")
    libs = getLibs(verbose=False)
    print('\n'.join(libs))

