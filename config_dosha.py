'''
Configuration file for the script generating hierarchical data
objects based on JMA landslide risk data set.

Reference on the technical elements:
 JMA Technical Report 374 (Japanese)
 http://www.data.jma.go.jp/add/suishin/jyouhou/pdf/374.pdf
'''

# Author: Matthew J. Holland, Osaka University


# Main user-defined constants.
FILE_NAME = "demo_datafile.h5"
FILE_TITLE = "Demonstration of full landslide risk data object."
DATA_TITLE = "Array storing numerical risk levels."
GRIDINFO_TITLE = "Grid coordinate information."
DATETIME_TITLE = "Date-time entries, with corresponding risk level entries."
VERBOSE = False

# Key facts to be hard-coded; likely no need to modify.
DATAFILE_HEADER = "Z__C_RJTD_"
NUMLAT = 560 # height of grid
NUMLON = 512 # width of grid
NUMCELLS= NUMLON*NUMLAT # multiply the dimensions of the lattice.
DEG_FIRSTLAT = 47.975
DEG_FIRSTLON = 118.03125
DEG_LASTLAT = 20.025
DEG_LASTLON = 149.96875
DEG_LATSIZE = 3.0/60
DEG_LONSIZE = 3.75/60
INFO_LIST = [DEG_FIRSTLAT, DEG_LASTLAT, DEG_LATSIZE,
             DEG_FIRSTLON, DEG_LASTLON, DEG_LONSIZE]
DATETIME_NUM = 5 # (YYYY, MM, DD, HH, NN)
DATETIME_SIZE = 4 # at most four ASCII characters.


