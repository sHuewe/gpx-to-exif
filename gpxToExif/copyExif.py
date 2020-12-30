import piexif, datetime
from PIL import Image
import glob
from xml.dom import minidom
from fractions import Fraction
import os

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def getPiexifGPS(lat, lng):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(0),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }
    return gps_ifd

def getTimeStampFromImage(image,timeZone):
 d=datetime.datetime.strptime(piexif.load(image.info["exif"])["Exif"][piexif.ExifIFD.DateTimeOriginal].decode(),"%Y:%m:%d %H:%M:%S")
 print(f'Date from image: {str(d)}')
 return d.timestamp()-timeZone*60*60

def getTimeStampFromGPX(timeField):
 try:
   d=datetime.datetime.strptime(timeField,"%Y-%m-%dT%H:%M:%SZ")
   print(f'Date from GPX with timezone: {str(d)}')
   return d.timestamp()#%Y-%m-%dT%H:%M:%SZ
 except:
   d=datetime.datetime.strptime(timeField,"%Y-%m-%dT%H:%MZ")
   print(f'Date from GPX: {str(d)}')
   return d.timestamp()#%Y-%m-%dT%H:%M:%SZ


def createThumb(path,out):
 with Image.open(path) as img:
  img.thumbnail((1000,1000))
  if out is not None:
   img.save(out)
 return ImageObject(path)

def getDateFromImage(image):
 return piexif.load(image.info["exif"])["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()


def hasGPS(image):
 return len(piexif.load(image.info["exif"])["GPS"])>0


def match(sourceFolder,targetFolder):
 sourceList=glob.glob(sourceFolder+"/*")
 for offset in [5]:#[0,1,3,5,7,10,20,30]:
  for sourcePath in sourceList:
   print(f'Read ')
   print(sourcePath)
   copyExif(sourcePath,targetFolder,offset=offset)

def cloneExif(wrapperSource,wrapperTarget,forceRemoveGPS=False):
    target=Image.open(wrapperTarget.path)
    tempExifData=piexif.load(target.info["exif"])
    if wrapperSource is None and forceRemoveGPS:
        tempExifData["GPS"]={}
    else:
        tempExifData["GPS"]=wrapperSource.GPSData
    piexif.insert(piexif.dump(tempExifData),wrapperTarget.path)
    wrapperTarget.init()

class ImageObject():
    def __init__(self,path,timeZone=2):
        self.path=path
        self.timeZone=timeZone
        self.init()

    def init(self):
        if self.path is None:
            return #GPX case
        #Check if image or gpx
        if self.path[-4:]==".gpx":
            self.hasGPS=False
            self.gpx=True
            return
        else:
            self.gpx=False
            img=Image.open(self.path)
            self.hasGPS=hasGPS(img)
            self.time=getTimeStampFromImage(img,self.timeZone)
            self.niceDate=getDateFromImage(img)
            if self.hasGPS:
                self.GPSData=piexif.load(img.info["exif"])["GPS"]

    def getNiceGPSData(self):
        if not self.hasGPS:
         return "no GPS Data available"
        lat=self.GPSData[piexif.GPSIFD.GPSLatitude]
        latString=str(int(lat[0][0]/lat[0][1]))+"°"+str(int(lat[1][0]/lat[1][1]))+"'"+str(lat[2][0]/lat[2][1])+"''"
        lng=self.GPSData[piexif.GPSIFD.GPSLongitude]
        lngString=str(int(lng[0][0]/lng[0][1]))+"°"+str(int(lng[1][0]/lng[1][1]))+"'"+str(lng[2][0]/lng[2][1])+"''"
        return "Latitude: "+latString+"\nLongitude:"+lngString

    def clone(self):
        return ImageObject(self.path)

    def isGpx(self):
        return self.gpx

    #TODO add other gpx types
    def getElementsFromGpx(self):
        xmldoc = minidom.parse(self.path)
        res=[]
        wayPointCount=0
        trackPointCount=0
        routePointCount=0
        for type_tag in  xmldoc.getElementsByTagName('wpt'):
            wayPointCount+=1
            newOb= ImageObject(None)
            newOb.hasGPS=True
            newOb.GPSData=getPiexifGPS(float(type_tag.attributes['lat'].value),float(type_tag.attributes['lon'].value))
            newOb.time=getTimeStampFromGPX(type_tag.getElementsByTagName("time")[0].firstChild.nodeValue)
            newOb.name=f'Waypoint {wayPointCount} from {os.path.basename(self.path)}'
            res.append(newOb)
        for type_tag in xmldoc.getElementsByTagName('trk'):
            name=""
            if len(type_tag.getElementsByTagName("name"))>0:
                name=type_tag.getElementsByTagName("name")[0].firstChild.nodeValue
            for seg_tag in type_tag.getElementsByTagName('trkseg'):
                for wp_tag in seg_tag.getElementsByTagName('trkpt'):
                    trackPointCount+=1
                    newOb= ImageObject(None)
                    newOb.hasGPS=True
                    newOb.GPSData=getPiexifGPS(float(wp_tag.attributes['lat'].value),float(wp_tag.attributes['lon'].value))
                    newOb.time=getTimeStampFromGPX(wp_tag.getElementsByTagName("time")[0].firstChild.nodeValue)
                    newOb.name=f'Point {trackPointCount} from track {name} from {os.path.basename(self.path)}'
                    res.append(newOb)
        for type_tag in xmldoc.getElementsByTagName('rte'):
            name=""
            if len(type_tag.getElementsByTagName("name"))>0:
                name=type_tag.getElementsByTagName("name")[0].firstChild.nodeValue
            for wp_tag in type_tag.getElementsByTagName('rtept'):
                    routePointCount+=1
                    newOb= ImageObject(None)
                    newOb.hasGPS=True
                    newOb.GPSData=getPiexifGPS(float(wp_tag.attributes['lat'].value),float(wp_tag.attributes['lon'].value))
                    newOb.time=getTimeStampFromGPX(wp_tag.getElementsByTagName("time")[0].firstChild.nodeValue)
                    newOb.name=f'Point {routePointCount} from route {name} from {os.path.basename(self.path)}'
                    res.append(newOb)

            
            
        return res

class ExifMatcher():

    sources=[]
    targets=[]

    def __init__(self,sourceFolderPath,targetFolderPath,timeZone=2):
        self.timeZone=timeZone
        print("Parse sources..")
        self.initFolder(sourceFolderPath,self.sources,True)
        print()
        print("Parse targets..")
        self.initFolder(targetFolderPath,self.targets,False)
        print()
        print()
        self.printOverview()

    def printOverview(self):

        print("report:")
        print()
        print("sources")
        for source in self.sources:
            print(str(source.name)+" "+str(source.hasGPS)+" "+str(source.time))
        print("")
        print("targets")
        for target in self.targets:
            print(target.path+" "+str(target.hasGPS)+" "+str(target.time))

    def initFolder(self,folderPath,objectList,requireGPS):
        fileList=glob.glob(folderPath+"/*")
        for filePath in fileList:
            wrapp=ImageObject(filePath,self.timeZone)
            wrappList=[wrapp]
            if wrapp.isGpx():
                wrappList=wrapp.getElementsFromGpx()
            for w in wrappList:
                if not requireGPS or w.hasGPS:
                    objectList.append(w)

    def matchNext(self,overwrite=True):
        timeList=[]

        for source in self.sources:
            timeList.append(source.time)
        for target in self.targets:
            if target.hasGPS and not overwrite:
                continue
            matchedSourceIndex=self.getMatchingSourceIndex(timeList,target)
            if matchedSourceIndex is not None:
                print("Best value for "+str(target.path)+": "+str(self.sources[matchedSourceIndex]))
                cloneExif(self.sources[matchedSourceIndex],target)
        return

    def getMatchingSourceIndex(self,timeList,target):
        minDelta=2*60*60+1
        for i in range(0,len(timeList)):
            delta=abs(timeList[i]-target.time)
            if delta<minDelta:
             minDelta=delta
             minSourceIndex=i
        if minDelta>2*60*60:
            return None
        return minSourceIndex

    def match(self):
        for source in self.sources:
            for target in self.targets:
                if target.hasGPS:
                    continue
                if abs(source.time - target.time)<3:
                    cloneExif(source,target)
                    target.hasGPS=True
                    print("Cloned from "+source.path+" to "+target.path)
                else:
                    print(f'{source.time} {target.time}')
