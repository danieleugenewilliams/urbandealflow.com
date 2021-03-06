'''
Copyright 2018 Daniel E. Williams (@dewilliams)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import xmltodict
import os
from os import listdir
from os.path import isfile, join
import csv
from bs4 import BeautifulSoup
import glob
import ntpath
from zipfile import ZipFile
import sys

def main():

    # set up paths and filenames
    zipdir = './test/'
    #zipdir = './census/zips/'
    zipfiles = glob.glob(zipdir + '*.zip')
    csvdir = './kml_csv/'
    csvout = "out.csv" 
    pmcount = 0

    # ensure paths exist, and if not mkdirs
    assurePathExists(zipdir)
    assurePathExists(csvdir)

    # loop through kml zipfiles
    for zipfile in zipfiles:
        zipbase = ntpath.basename(zipfile)
        kmlfile = zipbase[:len(zipbase)-3] + "kml"
        with ZipFile(zipfile, 'r') as z:
            for name in z.namelist():
                if(name == kmlfile):
                    data = z.read(name)
                    soup = BeautifulSoup(data, 'xml')
                    doc = xmltodict.parse(soup.prettify())
                    kmlrecord = []
        
                    pmcount = getPlacemarkCount(doc)
                    #print "Placemark count: " + str(pmcount)
                    for index in xrange(pmcount):
                        kmlrecord = []
                        kmlrecord.append(getSimpleData(doc, index, "STATEFP"))
                        kmlrecord.append(getSimpleData(doc, index, "COUNTYFP"))
                        kmlrecord.append(getSimpleData(doc, index, "TRACTCE"))
                        kmlrecord.append(getSimpleData(doc, index, "AFFGEOID"))
                        kmlrecord.append(getSimpleData(doc, index, "GEOID"))
                        kmlrecord.append(getSimpleData(doc, index, "NAME"))
                        kmlrecord.append(getSimpleData(doc, index, "LSAD"))
                        kmlrecord.append(getSimpleData(doc, index, "ALAND"))
                        kmlrecord.append(getSimpleData(doc, index, "AWATER"))
                        coord = getCoordinates(doc, index)
                        #print coord
                        if(coord):
                            kmlrecord.append(coord)
                        #print kmlrecord
                        
                        print "Index " + str(index) + " of " + str(pmcount)
                        #kmldata.append(kmlrecord)
                        writeKmlCsv(csvdir + kmlfile + csvout, kmlrecord)   

# output kml data to csv file
def writeKmlCsv(outputfile, data):
    with open(outputfile, "ab") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(data)

def assurePathExists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


# transform 3d coordinates to polygon format accepted by MySQL
def transform3DCoordToPolygon(coordinates):
    coordinates = coordinates.replace(",", " ")
    coordinates = coordinates.replace(" 0.0 ", ", ")
    coordinates = coordinates.replace(" 0.0", "") 
    return "'Polygon((" + coordinates + "))'"

# transform 3d coordinates to multipolygon format accepted by MySQL
def transform3DCoordToMultiPolygon(coordinates_array):
    multipolygon_str = ""
    for coord in coordinates_array:
        coord = coord.replace(",", " ")
        coord = coord.replace(" 0.0 ", ", ")
        coord = coord.replace(" 0.0", "")
        multipolygon_str += "((" + coord + ")),"
    multipolygon_str = multipolygon_str.rstrip(",")
    multipolygon_str = "'MultiPolygon(" + multipolygon_str + ")'"
    print multipolygon_str
    return multipolygon_str

# get count of placemarks
def getPlacemarkCount(doc):
    return len(doc['kml']['Document']['Folder']['Placemark'])

# get coordinates from kml from for a given placemark
def getCoordinates(doc, placemark_index):
    # polygon coordinates
    coord_array = []
    try: 
        return transform3DCoordToPolygon(doc['kml']['Document']['Folder']['Placemark'][placemark_index]['Polygon']['outerBoundaryIs']['LinearRing']['coordinates'])
    except:
        print "encountered an error getting placemark/polygon at " + getSimpleData(doc, placemark_index, "GEOID") 
        print "getting placemark/multigeometry/polygon"
        polygon_count = len(doc['kml']['Document']['Folder']['Placemark'][placemark_index]['MultiGeometry']['Polygon'])
        for polygon_index in xrange(polygon_count):
            coord_array.append(doc['kml']['Document']['Folder']['Placemark'][placemark_index]['MultiGeometry']['Polygon'][polygon_index]['outerBoundaryIs']['LinearRing']['coordinates'])
        return transform3DCoordToMultiPolygon(coord_array)

# Data Names and Example Data
# @name = STATEFP = 01
# @name = COUNTYFP = 001
# @name = TRACTCE = 020200
# @name = AFFGEOID = 1400000US01001020200
# @name = GEOID = 01001020200
# @name = NAME = 202
# @name = LSAD = CT
# @name = ALAND = 3325679
# @name = AWATER = 5670
def getSimpleData(doc, placemark_index, data_name):
    simple = doc['kml']['Document']['Folder']['Placemark'][placemark_index]['ExtendedData']['SchemaData']['SimpleData']
    for x in xrange(len(simple)):
        if(simple[x]['@name'] == data_name):
            return "'" + str(simple[x]['#text']) + "'"



# this is the standard boilerplate that calls the main() function
if __name__ == '__main__':
    # sys.exit(main(sys.argv)) # used to give a better look to exists
    main()


