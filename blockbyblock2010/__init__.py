#!/usr/bin/env python
from __future__ import print_function
import csv
import shapefile
import timeit
import heapq


import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib.colors as colors
import matplotlib.cm as cm



class GeoHeader:
    """
    This object contains select data from the geo header file of the sf1 file. The only argument
    is the path to the geo header. Each property is ordered by the LOGRECNO
    """
    def __init__(self, geo_path):
        
        
        #
        #load geo file, and use geo_column to collect relavent info
        #
        self.geo_header_file=[]
        #copy contents of the header into self.geo_header_file
        with open(str(geo_path),'rt') as f:
            reader = csv.reader(f,delimiter='*', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                self.geo_header_file.append(row)
                
        ## Selected data points
        self.sumlev = self.geo_column(9,3, return_numbers=False)#summary level
        self.logrecno = self.geo_column(19,7, return_numbers = True)
        self.state_county = self.geo_column(28,5,return_numbers = False) # state and county
        self.census_tract = self.geo_column(55,6,return_numbers = False) # census tract
        self.block_group = self.geo_column(61,1,return_numbers = False) # block group
        self.block = self.geo_column(62,4,return_numbers = False) # block

        #position
        self.lat = self.geo_column(337,11)
        self.lon = self.geo_column(348,12)
        
        #AREA CHARACTERISTICS
        self.area_land = self.geo_column(199,14, return_numbers = True) #AREALAND
        self.area_water = self.geo_column(213,14, return_numbers =True ) #AREAWATR
        self.pop100 = self.geo_column(319,9, return_numbers = True) #POP100
        self.housing_units = self.geo_column(328,9, return_numbers =True ) #HU100

        self.geo_header_file=None #free up some memory
        
        #
        #Done with the geo_column function, and the geo_header_file
        #
        
        #The geoid is constructed from the state, county, census tract and block
        self.geoid = []
        for i in range(len(self.logrecno)):
            self.geoid.append(self.state_county[i]+self.census_tract[i]+self.block[i])
            
        self.state_county, self.census_tract,self.block=None,None,None
        
        
        self.length = len(self.logrecno)
        self.rang = range(len(self.logrecno))


        #make a dictionary for logrecno -> geoid
        self.logrecdict=dict()
        self.pop100dict=dict()
        for logrecno, geoid,pop100 in zip(self.logrecno,self.geoid,self.pop100): 
            self.logrecdict[geoid]=logrecno
            self.pop100dict[geoid]=pop100


        self.geodict=dict()
        for logrecno, geoid in zip(self.logrecno,self.geoid):
            if geoid[0]!=' ':
                self.geodict[logrecno]=geoid
                
    def geo_column(self,starting_position, field_size, return_numbers = True):
        """This function returns a list for the given column in the geo header file. 
        The starting position is the starting record number, as in the data dictionary 
        (which starts at 1)"""
        col_start = starting_position-1 
        # 1 is subtracted to convert from the data dictionary start to a list index
        out=[]
        col_end=col_start+field_size #field size from the data dictionary

        if return_numbers == True:
            for row in self.geo_header_file:
                try:
                    out.append(float(str(row[0][col_start:col_end])))
                except ValueError:
                    out.append(str(row[0][col_start:col_end]))
        else:
            out=[]
            for row in self.geo_header_file:
                out.append(str(row[0][col_start:col_end]))
        return out
                
class sf1Reader():
    """
    Class used for reading data from sf1 files.
    
    :Parameters:

        sf1_path:string

        state_string:string 
            the two letter lower case abbreviation for the. eg 'ny'
    
    :Methods:
        read()
    
    :Members:
        Data_Dict:dictionary
            Keys are Census data codes and values are file number and column position.    
    
    """
    def __init__(self, sf1_path='default',state=''):
        """
        creates the code dictionary, and initializes the path for sf1 files

        """
        self.state=state
        self.sf1_path=sf1_path


        #
        #Data dictionary
        #
        self.description=[] #copy the file to self.description
        with open(descriptor_path,'rt') as f:
            reader = csv.reader(f,delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                self.description.append(row)
                
        self.codedict = dict()
        self.heading_number=0
        self.heading=list()
        segment = 0 #this is equivalent to the segment of the sf1 file 
        record = 5 #the record in the sf1 file 
        for row,i in zip(self.description[1:],range(len(self.description))[1:]):
            if int(row[1]) > segment:
                segment += 1
                record = 5
            if (row[4]==''):
                if self.description[i-1][4]=='':
                    self.heading[self.heading_number-1].append(row[3])
                    
                else:
                    self.heading.append([row[3]])
                    self.heading_number += 1
            if row[4] != '': #row[1] is the segment, row[4] is the field code
                self.codedict[row[4]] = (row[1],record)
                self.heading[self.heading_number-1].append([row[3],row[4]])
                record += 1


                
                
    #Reads the given sf1 file, and outputs specified column to a numpy array
    def read(self,field_code, return_numbers=True):
        """
        Takes as an input the state and sf1 field code.

        Returns a dictionary in which the keys are logical record numbers
        and the values are the values for the sf1 field. 

        :Parameters:
            Field_Code:string
                The census field code as described in the Data Field Descriptors.txt
                or the sf1 documentation
            return_numbers:boolean
                If true, returns dictionary with float values. If false, string values.

        :Returns:
            out:dictionary
                Dictionary with Logical record numbers as keys, and the requested data
                for each logrecno as the value. 
        """
        start_time = timeit.default_timer()
        sf1=[]
        segment,column = self.codedict[field_code]
 
        #read document into sf1
        with open(self.sf1_path+self.state+'000'+\
                      segment.zfill(2)+'2010.sf1','rt') as f:
            reader = csv.reader(f,delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                sf1.append(row)



        data=[]
        logrecno=[]
        for line in sf1:
            data.append(line[column])
            logrecno.append(line[4])

        out=dict()
        for datum,num in zip(data,logrecno):
            if return_numbers==True:
                out[int(num)]=float(datum)
            else:
                out[int(num)]=datum
        return out
                
                
                
                

                
                
class StateHeaderAndShape:
    """
    This class creates an object for each state, which contains all geographic information
    
    geo_header_file is the raw data from the geo header within the sf1 package

    header is selected data from the header file.
    Most importantly, it has the following dictionaries:
        geo_dict
        logrecno_dict
        
    
    string is the two character string for the state, which is used in file paths
    
    xy contains every polygon within the shape file
    :Parameters:
        state:string
            two letter lower case abbreviation
        state_num:string
            two digit FIPS number
            
        census2010folder:string
            the path where the state folders are located. Used to locate shape, 
            and sf1 paths. If those other paths are defined, then this path is useless
            
        sf1_path:
            the path where the sf1 file is located
        
        shape_path:
            the path where the shapefile is located
        
    """
    def __init__(self,state,  shape_path='default',sf1_path='default'):

        self.string = state

        #
        #setting up paths
        #
            
        self.sf1=sf1Reader(state=self.string, sf1_path=sf1_path)
        

        #from here, the geo header file is read
        geo_path=sf1_path+state+'geo2010.sf1'
        self.header = GeoHeader(geo_path)
        
        
        #
        #     
        #       
        #READ SHAPEFILE
        start_time = timeit.default_timer()

        self.dat=shapefile.Reader(shape_path)
        self.info=dict()
        for i in range(len(self.dat.fields)-1):
            self.info[self.dat.fields[i+1][0]]=i
        
        
        #copy the shape data into xy, xy_info and xy_geoid
        #xy_geoid info is contained in xy_info, but the lists are sorted
        #using xy_geoid, so that a binary search can be used when making a map
        self.xy=[]
        self.xy_info=[]
        self.xy_geoid=[]
        self.area = []
        for shape, data in zip(self.dat.shapes(),self.dat.records()):
            if data[self.info['ALAND10']]>0: # eliminates places with no land.
                for i in range(len(shape.parts)): 
                    #shape.parts contains the starting points for each polygon within the points
                    #this for loop creates every polygon to be mapped
                    self.xy_geoid.append(data[self.info['GEOID10']].ljust(15))
                    self.area.append(int(data[self.info['ALAND10']]))
                    if shape.parts[i] == shape.parts[-1]:
                        self.xy.append(shape.points[shape.parts[i]:])
                    else:
                        self.xy.append(shape.points[shape.parts[i]:shape.parts[i+1]])
        self.dat=None
                
        #END shapefile reading
        #
        #
        #
        
        print("read header and shapefiles in "+str(
            timeit.default_timer() - start_time)[0:3]+'s')
        
def plot_map(place,datacode='P0010001',axes=[],size=10,bg=(0,0,0),
             cmap=cm.ocean,vmax='', vmaxpercentile=0.1,vminpercentile='min',alpha=1, density=False,
             percentage=False, return_data=False,save=''):
    """
    takes a list of StateHeaderAndShape objects, and a sf1 data code, and plots a map
    using the PolyCollection class from matplotlib.collections
    
    :Parameters:
        place:list of StateHeaderAndShape instances
        
        data:string
            the census datacode fed into the sf1reader.read method
        
        axes:list
            longitude min, longitude max, lattitude min, lattitude max
        
        size:int or tuple
            fed into plt.figure(figsize=size)
            
        bg:tuple, string or other MPL-recognized color code
            background color
            
        cmap: matplotlib colormap instance
        
        vmax:string or float
            this is the value used in the matplotlib normalize function. 
            values greater than vmax will be colored the same as vmax
            '' is used for vmaxpercentile instead
            
        vmaxpercentile:float or string
            'max' will set vmax as the maximum value in the dataset
            float will be the percentile/100 (eg, 0.01 vmax the top 1%)
        
        return_data:boolean
            if true, will return a list containing the shapes list and the data list
            will not draw the map or make the polygoncollection
    """
    start_time = timeit.default_timer()

    data=[]
    shapes=[]
    for state in place:
        statedata=[]
        
        if type(datacode) is str:
            rawdata=state.sf1.read(datacode)
        if type(datacode) is dict:
            rawdata=datacode
        newshapes=[]
        stateArea=[]
        stateGEOIDs=[]
        for (geoid,newplace, area) in zip(state.xy_geoid,state.xy,state.area):
            if type(datacode) is str:
                key=state.header.logrecdict[geoid]
            if type(datacode) is dict:
                key=geoid
            if axes != []:
                if (axes[2]-.5<newplace[0][1]<axes[3]+.5) and (axes[0]-.5<newplace[0][0]<axes[1]+.5):
                    statedata.append(rawdata[key])
                    newshapes.append(newplace)
                    stateGEOIDs.append(geoid)
                    stateArea.append(area)
            if axes == []:
                statedata.append(rawdata[key])
                newshapes.append(newplace)
                stateGEOIDs.append(geoid)
                stateArea.append(area)

        if density==True:
            new_data=[]
            for item, area in zip(statedata, stateArea):
                new_data.append(float(item)/float(area))
            statedata=new_data
        if percentage==True:
            new_data=[]
            excepts=0
            for datum, geoid in zip(statedata, stateGEOIDs):
                try:
                    new_data.append(float(datum)/float(state.header.pop100dict[geoid]))
                except ZeroDivisionError:
                    excepts+=1
                    new_data.append(0.)
            statedata=new_data


        shapes=shapes+newshapes
        data=data+statedata
        
    #print("parsed sf1 file in "+str(
    #    timeit.default_timer() - start_time)[0:3]+'s')
        
      
    if return_data==True:
        return [shapes,data]
    #
    #The actual plotting:
    #
    # Vmax is the largest value used for coloring polygons if vmaxpercentile is used,
    # Then vmax is calculated using heapq
    #
    # this is the default maximum value for coloring the data. heapq.nlargest makes a list 
    # of values in the percentile given. The lowest of those is then chosen as the max color value.
    if type(vmax) is float:
        vmaxpercentile=''
    if type(vmaxpercentile) is float:
        vmax = heapq.nlargest(int(vmaxpercentile*len(data)),data)[int(vmaxpercentile*len(data))-1]
        print(str("Values above ")+str(vmax*2.59*10**6)+' people per sq mile are treated the same')
    if vmaxpercentile is 'max':
        vmax = max(data)
        print(str("The largest value is ")+str(vmax*2.59*10**6)+'people per sq mile')
    if percentage==True:
        vmin=0
        vmax=1
        

    if vminpercentile is 'min':
        vmin = 0
    if type(vminpercentile) is float:
        vmin = heapq.nsmallest(int(vminpercentile*len(data)),data)[0]

        
        
    norm = colors.Normalize(vmin,vmax,clip=True)
    poly = PolyCollection(shapes,color=cmap(norm(data)),alpha=alpha)
    
    if return_data==True:
        return [shapes,data]
    
    fig=plt.figure(figsize=size)
 
    ax = plt.subplot(1,1,1, axisbg = bg)

    plt.gca().add_collection(poly);
    if axes==[]:
        plt.autoscale()
    else:
        plt.axis(axes)

    if save is not '':
        plt.savefig(save)
    if save is '':
        plt.show()

descriptor_path=__file__.rstrip('__init__.py')+'DATA_FIELD_DESCRIPTORS.txt'
