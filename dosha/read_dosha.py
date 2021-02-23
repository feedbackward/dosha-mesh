'''
Reading and processing the landslide risk levels published
by the Japan Meteorological Agency (JMA) in the binary
FM92 GRIB format.

Reference on the technical elements:
 JMA Technical Report 374 (Japanese)
 http://www.data.jma.go.jp/add/suishin/jyouhou/pdf/374.pdf
'''

# Author: Matthew J. Holland, Osaka University


import numpy as np

class DoshaMesh:

    def __init__(self, filename, verbose=False):

        self.filename = filename
        self.checker(verbose=verbose)

        if verbose:
            print("Offsets:")
            print(self.offsets)

        self.data_info(verbose=verbose)
        self.data_read(verbose=verbose)
        self.data_decompress(verbose=verbose)


    def checker(self, verbose=False):
        '''
        Runs a quick scan to ensure the data is
        of the expected form.
        '''
        f_bin = open(self.filename, mode="rb")

        # Sec 0 checks.
        b = f_bin.read(4) # Should be "GRIB".
        if str(b, 'ascii') != "GRIB":
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")
        s0_seclen = 16 # hard-coded.
        
        # Sec 1 checks.
        f_bin.seek(s0_seclen)
        b = f_bin.read(4) # should be 21.
        s1_seclen = int.from_bytes(b, byteorder="big", signed=False)
        if s1_seclen != 21:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")

        # Sec 2 is not used.
        # Sec 3 checks.
        f_bin.seek((s0_seclen+s1_seclen))
        b = f_bin.read(4) # Should be 72.
        s3_seclen = int.from_bytes(b, byteorder="big", signed=False)
        if s3_seclen != 72:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")


        # Sec 4 checks.
        f_bin.seek((s0_seclen+s1_seclen+s3_seclen))
        b = f_bin.read(4) # Should be 42.
        s4_seclen = int.from_bytes(b, byteorder="big", signed=False)
        if s4_seclen != 42:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")

        # Sec 5 checks.
        f_bin.seek((s0_seclen+s1_seclen+s3_seclen+s4_seclen))
        b = f_bin.read(4) # will be variable, can't use for checking.
        s5_seclen = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(1) # Should be 5 (the section number).
        s5_secnum = int.from_bytes(b, byteorder="big", signed=False)
        if s5_secnum != 5:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")

        # Sec 6 checks.
        f_bin.seek((s0_seclen+s1_seclen+s3_seclen+s4_seclen+s5_seclen))
        b = f_bin.read(4) # Should be 6.
        s6_seclen = int.from_bytes(b, byteorder="big", signed=False)
        if s6_seclen != 6:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")

        # Sec 7 checks.
        f_bin.seek((s0_seclen+s1_seclen+s3_seclen\
                    +s4_seclen+s5_seclen+s6_seclen))
        b = f_bin.read(4) # will be variable, can't use for checking.
        s7_seclen = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(1) # Should be 7 (the section number).
        s7_secnum = int.from_bytes(b, byteorder="big", signed=False)
        if s7_secnum != 7:
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")

        # Sec 8 checks.
        f_bin.seek((s0_seclen+s1_seclen+s3_seclen\
                    +s4_seclen+s5_seclen+s6_seclen+s7_seclen))
        b = f_bin.read(4) # Should be "7777", string.
        if str(b, 'ascii') != "7777":
            raise ValueError("Format issue.")
        elif verbose:
            print("clear!")
        
        
        # If make it to the end, save the sec lengths.
        self.s0_seclen = s0_seclen
        self.s1_seclen = s1_seclen
        self.s2_seclen = 0
        self.s3_seclen = s3_seclen
        self.s4_seclen = s4_seclen
        self.s5_seclen = s5_seclen
        self.s6_seclen = s6_seclen
        self.s7_seclen = s7_seclen
        self.s8_seclen = 4

        self.seclengths = [self.s0_seclen,
                           self.s1_seclen,
                           self.s2_seclen,
                           self.s3_seclen,
                           self.s4_seclen,
                           self.s5_seclen,
                           self.s6_seclen,
                           self.s7_seclen,
                           self.s8_seclen]

        offset = 0
        self.offsets = []
        for s in range(9):
            self.offsets += [offset]
            offset += self.seclengths[s]

        f_bin.close()


    def data_info(self, verbose=False):
        '''
        Get key data-related information.
        '''

        if verbose:
            print("Read data info...")
        
        f_bin = open(self.filename, mode="rb")

        # Key quantities for decompressing the data.
        f_bin.seek(self.offsets[5]+11)
        b = f_bin.read(1)
        self.s5_databits = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(2)
        self.s5_V = int.from_bytes(b, byteorder="big", signed=False)
        #print(self.s5_databits, self.s5_V)

        # Dimensions of the grid.
        f_bin.seek(self.offsets[3]+46)
        b = f_bin.read(4) # Should be 47975000.
        self.s3_firstlat = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(4) # Should be 118031250.
        self.s3_firstlon = int.from_bytes(b, byteorder="big", signed=False)

        f_bin.read(1) # skip this octet.
        
        b = f_bin.read(4) # Should be 20025000.
        self.s3_lastlat = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(4) # Should be 149968750.
        self.s3_lastlon = int.from_bytes(b, byteorder="big", signed=False)

        b = f_bin.read(4) # Should be 62500.
        self.s3_isize = int.from_bytes(b, byteorder="big", signed=False)
        b = f_bin.read(4) # Should be 50000.
        self.s3_jsize = int.from_bytes(b, byteorder="big", signed=False)

        # # Latitude (working N-->S)
        self.deg_firstlat = self.s3_firstlat/10**6
        self.deg_lastlat = self.s3_lastlat/10**6
        self.deg_latsize = self.s3_jsize/10**6
        self.deg_lat = np.arange(self.deg_firstlat,
                                 self.deg_lastlat-0.0001,
                                 -self.deg_latsize)
        # # Longitude (working W-->E)
        self.deg_firstlon = self.s3_firstlon/10**6
        self.deg_lastlon = self.s3_lastlon/10**6
        self.deg_lonsize = self.s3_isize/10**6
        self.deg_lon = np.arange(self.deg_firstlon,
                                 self.deg_lastlon+0.0001,
                                 self.deg_lonsize)

        self.gridshape = (self.deg_lat.size, self.deg_lon.size)
        
        f_bin.close()


    def data_read(self, verbose=False):
        '''
        Read out the raw data.
        '''

        if verbose:
            print("Read the compressed data...")
        
        f_bin = open(self.filename, mode="rb")

        f_bin.seek(self.offsets[7]+5)

        # number of bytes left in this section.
        bytes_left = self.s7_seclen - 5
        # Before doing anything, read out the compressed data sequence.
        self.data_compressed = []
        bpd = self.s5_databits // 8 # bytes per data point.
        for i in range(bytes_left):
            b = f_bin.read(bpd)
            #print("bytes:", b)
            b_int = int.from_bytes(b, byteorder="big", signed=False)
            self.data_compressed += [b_int]

        f_bin.close()
        

    def data_decompress(self, verbose=False):
        '''
        Decompress the compressed data
        '''

        if verbose:
            print("Prepare the decompressed data...")
        
        tmp_data = self._decompress(data_compressed=self.data_compressed,
                                    NBIT=self.s5_databits,
                                    MAXV=self.s5_V)
        self.Xgrid = np.array(tmp_data).reshape(self.gridshape)
        self.Xgrid = self.Xgrid - 3
        self.Xgrid[self.Xgrid < 0] = 99 # all non-negative now.
        self.Xgrid = np.uint8(self.Xgrid)


    def _decompress(self, data_compressed, NBIT, MAXV, verbose=False):
        '''
        The workhorse routine, for run-length compressed data.
        '''
        LNGU = 2**NBIT-1-MAXV
        
        data_decompressed = []
        dictpair = {"data": [], "runlen": []}
        for i in range(len(data_compressed)):
    
            tocheck = data_compressed[i]
            if verbose:
                print("tocheck =", tocheck, "; dict =", dictpair)
    
            if len(dictpair["data"]) == 0:
                dictpair["data"] = [tocheck]
            else:
                # If data slot is populated, then we're either dealing
                # with runlength, or moving to a new singleton.
        
                if tocheck > MAXV:
                    # In this case, it is runlength data to be added.
                    dictpair["runlen"] += [tocheck]
                else:
                    # In this case, it is data, signifying a new set.
                    # Thus, we must enter the "processing" routine.
            
                    numrl = len(dictpair["runlen"])
                    if numrl == 0:
                        # If no runlength info, means it only appeared once.
                        data_decompressed += dictpair["data"]
                        if verbose:
                            print("Adding to decompressed data:", dictpair["data"])
                
                    else:
                        # If there is runlength info, then must process it.
                        rlinfo = np.array(dictpair["runlen"])
                        rlexp = np.arange(numrl)
                        rlvec = (LNGU**rlexp) * (rlinfo - (1+MAXV))
                        rl = np.sum(rlvec) + 1
                        data_decompressed += rl * dictpair["data"]
                        if verbose:
                            print("Adding to decompressed data:", rl * dictpair["data"])
            
                    # Reset, noting that we have a new data point to store.
                    dictpair["data"] = [tocheck]
                    dictpair["runlen"] = []


        # Finally, note that there will ALWAYS be something left over.
        if tocheck <= MAXV:
            # If the last guy was small, then just add it.
            data_decompressed += dictpair["data"]
            if verbose:
                print("Adding to decompressed data:", dictpair["data"])
        else:
            # If the last guy was large, we have non-trivial run-length.
            numrl = len(dictpair["runlen"])
            rlinfo = np.array(dictpair["runlen"])
            rlexp = np.arange(numrl)
            rlvec = (LNGU**rlexp) * (rlinfo - (1+MAXV))
            rl = np.sum(rlvec) + 1
            data_decompressed += rl * dictpair["data"]
            if verbose:
                print("Adding to decompressed data:", rl * dictpair["data"])

        return data_decompressed


def datetime(dt):
    '''
    Given a date-time vector, return nicely formatted
    string of date and time.
    '''
    out = dt[0]+"/"+dt[1]+"/"+dt[2]+" "+dt[3]+":"+dt[4]
    return out
    
