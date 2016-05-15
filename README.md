Blockbyblock2010 is a python module for analyzing 2010 census data. It's especially useful for generating images using block-level data.

The ipython notebook blockbyblock2010examples.ipynb provides examples of use.

####System requirements:
1. Pyshp and Matplotlib libraries
2. For a large state like New York, at least 4GB of RAM is needed

####Installation:
Either keep the blockbyblock directory in the working directory, or move it to the site packages directory.

####Data needed:
This  notebook requires downloading each file for states of interest: 

1. The [sf1](http://www2.census.gov/census_2010/04-Summary_File_1/) file.

2. The [shapefile](http://www2.census.gov/geo/tiger/TIGER2010/TABBLOCK/2010/) tl_2010_xx_tabblock10.zip, where xx is the two digit [FIPS code](http://www.census.gov/geo/reference/ansi_statetables.html) for the state. 

3. [Data Dictionary](https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1) to reference the data. For example, 'P0010001' is the code for total population.

####CLASSES:
The **StateHeaderAndShape** class contains all shapefile data such as StateHeaderAndShape.xy and StateheaderAndShape.xy_geoid. These are from the TIGER shapefile alone. It also contains **sf1Reader** and  **GeoHeader** instances as **StateHeaderAndShape.sf1** and **StateHeaderAndShape.header.**

When creating a StateHeaderAndShape object, the arguments need are:
* state_string. The lower case two letter abbreviation for the state
* shape_path: The path to the shapefile
* sf1_path: the path to the sf1 file
* descriptor_path, if the data_descriptor.text is not in the working directory

Each object takes a significant chunk of memory, since it's loading every single block of the state into the memory. On a computer with a AMD FX-6300 CPU and 16gb of RAM and Linux Mint 17.1, Rhode Island takes about 3 seconds to load, while New York takes a minute.


The **GeoHeader** class takes a path to an sf1 file as a parameter, and is parses the geographic data within the sf1 file. It is primarily used for the GeoHeader.geodict dictionary, which converts geoIDs to logicalrecordnumbers.

The **sf1Reader** class takes a path to an sf1 file, and is used to parse the census data. The *read* method takes a census datareturns a dictionary that has logical record numbers as keys, and the census datum as the value.

####METHODS:
The **plot_map** function is used to output a matplotlib drawing of the sf1 data.

