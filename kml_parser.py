import xmltodict
from os import listdir
from os.path import isfile, join
import csv
from bs4 import BeautifulSoup

def main():

    kmlout = "out.csv" 
    mypath = "/path/to/kml/files/"
    kmlfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    kmldata = []
    pmcount = 0

    for kmlfile in kmlfiles:
        print "parsing " + mypath + kmlfile
        with open(mypath + kmlfile, 'rt') as fd:
            soup = BeautifulSoup(fd.read(), 'xml')
        doc = xmltodict.parse(soup.prettify())
        kmlrecord = []

        pmcount = getPlacemarkCount(doc)
        #print "Placemark count: " + str(pmcount)
        for index in xrange(pmcount):
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
                kmlrecord.append(transform3DCoordToPolygon(coord))
            #print kmlrecord
            print "Index " + str(index) + " of " + str(pmcount)
            #kmldata.append(kmlrecord)
            writeKmlCsv(kmlfile + kmlout, kmlrecord)   
 
# output kml data to csv file
def writeKmlCsv(outputfile, data):
    with open(outputfile, "ab") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(data)

# transform 3d coordinates to polygon format accepted by MySQL
def transform3DCoordToPolygon(coordinates):
    coordinates = coordinates.replace(",", " ")
    coordinates = coordinates.replace(" 0.0 ", ", ")
    coordinates = coordinates.replace(" 0.0", "") 
    return "Polygon((" + coordinates + "))"

# get count of placemarks
def getPlacemarkCount(doc):
    return len(doc['kml']['Document']['Folder']['Placemark'])

# get coordinates from kml from for a given placemark
def getCoordinates(doc, placemark_index):
    # polygon coordinates
    try: 
        return doc['kml']['Document']['Folder']['Placemark'][placemark_index]['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
    except:
        return None

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
            return simple[x]['#text']



# this is the standard boilerplate that calls the main() function
if __name__ == '__main__':
    # sys.exit(main(sys.argv)) # used to give a better look to exists
    main()


