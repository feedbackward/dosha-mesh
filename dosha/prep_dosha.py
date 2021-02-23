'''
Basic script for generating hierarchical data objects composed
of an arbitrary number of landslide risk level observations.
Key assumptions:

 1. Data files have the following nomeclature:
      Z__C_RJTD_YYYYMMDDHHNN00_MET_INF_Jdosha_Ggis5km_ANAL_grib2.bin
    where YYYY, MM, DD, HH, NN are respectively year, month, day,
    hour, and minutes.

 2. Directories are provided in proper chronological order.

Reference on the technical elements:
 JMA Technical Report 374 (Japanese)
 http://www.data.jma.go.jp/add/suishin/jyouhou/pdf/374.pdf
'''

# Author: Matthew J. Holland, Osaka University


import sys
import tables
import numpy as np
import os

from read_dosha import DoshaMesh
import config_dosha as CF

# FILE INFO ETC.
s = sys.stdin.read()
if (s.split(" ") == ""):
    raise ValueError("Please provide at least one directory.")
else:
    DIR_TOREAD = s.split(" ")

if CF.VERBOSE:
    print("Directories to be read:")
    print(DIR_TOREAD)


##### Initialize the file. #####

# Open file connection, writing new file to disk.
myh5 = tables.open_file(CF.FILE_NAME, mode="w", title=CF.FILE_TITLE)

# Create the EArray for actual values.
a = tables.UInt8Atom()
myh5.create_earray(myh5.root,
                   name="riskLevels",
                   atom=a,
                   shape=(0,CF.NUMLAT,CF.NUMLON),
                   title=CF.DATA_TITLE)

# Create the EArray for grid information, and populate it.
a = tables.Float64Atom()
myh5.create_earray(myh5.root,
                   name="gridInfo",
                   atom=a,
                   shape=(0,len(CF.INFO_LIST)),
                   title=CF.GRIDINFO_TITLE)
mydatum = np.array([CF.INFO_LIST]) # Note extra dimension, for enumeration.
myh5.root.gridInfo.append(mydatum)

# Create the EArray for date-time information.
a = tables.StringAtom(itemsize=CF.DATETIME_SIZE)
myh5.create_earray(myh5.root,
                   name="dateTime",
                   atom=a,
                   shape=(0,CF.DATETIME_NUM),
                   title=CF.DATETIME_TITLE)
if CF.VERBOSE:
    print("HDF5 object before being populated:")
    print(myh5)


##### Loop over the specified directories.  #####

idxstart = len(CF.DATAFILE_HEADER)

# Outer loop is over per-date folders.
for d in range(len(DIR_TOREAD)):
    
    mydir = DIR_TOREAD[d]
    list_file = os.listdir(DIR_TOREAD[d])
    list_file.sort()

    # Inner loop is over files in given folder.
    for f in list_file:

        if CF.VERBOSE:
            print("dir =", mydir, " | file =", f)
            print("Year:", yyyy, "Month:", mm, "Day:", dd,
                  "Hours:", hh, "Minutes:", nn)

        # Extract meta data from file name.
        fsub = f[idxstart:(idxstart+12)]
        #print(fsub)
        yyyy = fsub[0:4]
        mm = fsub[4:6]
        dd = fsub[6:8]
        hh = fsub[8:10]
        nn = fsub[10:12]
        
        mylist = [yyyy, mm, dd, hh, nn]
        mydatum = np.array([mylist]) # Note extra dimension, for enumeration.
        myh5.root.dateTime.append(mydatum)


        if CF.VERBOSE:
            print("Opening and decompressing data file...")
        # Next is to read and decompress the data.
        toread = os.path.join(mydir, f)
        myDoshaMesh = DoshaMesh(toread, verbose=CF.VERBOSE)
        if CF.VERBOSE:
            print("... extraction complete.")

        # Run a check on the data dimensions, ensure they are as expected.
        cond_lat = len(myDoshaMesh.deg_lat) != CF.NUMLAT
        cond_lon = len(myDoshaMesh.deg_lon) != CF.NUMLON
        if cond_lat or cond_lon:
            ValueError("Config file lat and lon do not match data object.")
        
        # If dimensions look all clear, append the data.
        mydatum = np.array([myDoshaMesh.Xgrid])
        myh5.root.riskLevels.append(mydatum)
        

# Close the file connection.
myh5.close()

if CF.VERBOSE:
    print("HDF5 object after being populated:")
    print(myh5)
