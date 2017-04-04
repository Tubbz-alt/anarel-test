# anarel-test
Repository to test conda based LCLS ana release system. This is an integration test, after all the packages are installed, make sure various things still work.

Run test_conda -h from this repo for help. When we test the conda environments built with the [anarel-manage](https://github.com/slaclab/anarel-manage) code, we typically execute this command
```
   test_conda --imports --libs --bins --pkgs --pkglist all 
```
This reads the [testdb.yaml](https://github.com/slaclab/anarel-test/blob/master/testdb.yaml) file, which has a sections for bins, libs, imports, and packages. It tests for the presence of each bin by running it with the -h option. It imports all the python modules listes, and dynamically loads the library files.

For the packages, you list which packages you want to test via what commands, for instance you might want to do the 'fast' nose tests for numpy.

