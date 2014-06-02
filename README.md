gWTO2
=====

## gui What To Observe 2, Cycle 2 version

Under GNU License.
Currently runs on linux systems with python2.7.x versions

Required libraries:

* cx_Oracle
* numpy
* pandas
* pyephem
* PyQt4

### readArchive.py

This library connects directly to the archive. We want to avoid using all.sbinfo
file, which is unstable and updates only once a day. In fact, this script will 
create all.sbinfo

### pwvdatos.pandas

Pandas dataframe file, with oppacities for pwv-frequency pairs.
