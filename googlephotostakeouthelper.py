import datetime
import glob
import json
import os
import piexif
import shutil
'''
pip install piexif 
'''

'''
{
  "title": "IMG_2847.JPG",
  "description": "",
  "imageViews": "50",
  "creationTime": {
    "timestamp": "1487453411",
    "formatted": "Feb 18, 2017, 9:30:11 PM UTC"
  },
  "photoTakenTime": {
    "timestamp": "1475521836",
    "formatted": "Oct 3, 2016, 7:10:36 PM UTC"
  },
  "geoData": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "geoDataExif": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },  
  "people": [{
    "name": "Moms"
  }],
  "archived": true,
  "url": "https://photos.google.com/photo/abc",
  "googlePhotosOrigin": {
    "mobileUpload": {
      "deviceType": "IOS_PHONE"
    }
  }
}
'''


import datetime
import glob
import json
import os
import piexif
import fractions


#helper methods
#https://stackoverflow.com/a/77056370
def deg_to_dms(decimal_coordinate, cardinal_directions):
    if decimal_coordinate < 0:
        compass_direction = cardinal_directions[0]
    elif decimal_coordinate > 0:
        compass_direction = cardinal_directions[1]
    else:
        compass_direction = ""
    degrees = int(abs(decimal_coordinate))
    decimal_minutes = (abs(decimal_coordinate) - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = fractions.Fraction((decimal_minutes - minutes) * 60).limit_denominator(100)
    return degrees, minutes, seconds, compass_direction
def dms_to_exif_format(dms_degrees, dms_minutes, dms_seconds):
    exif_format = (
        (dms_degrees, 1),
        (dms_minutes, 1),
        (int(dms_seconds.limit_denominator(100).numerator), int(dms_seconds.limit_denominator(100).denominator))
    )
    return exif_format

for filePath in glob.iglob("D:\\takeout-20240104T140745Z-001\\Takeout\\Google Photos\\Photos from 1990" + '**/**', recursive=True):
    if filePath.endswith("json"):
        jsonData = None
        fileName = None
        with open(filePath, 'r') as f:
            jsonData = json.load(f)
        
        rootPath = os.path.dirname(filePath)
        
        if 'title' in jsonData:
            fileName = jsonData['title']
        else:
            continue
        
        #check if file in parent directory
        if fileName in os.listdir(rootPath):
            #load the exif data
            exif_dict = piexif.load(os.path.join(rootPath, fileName))
            #if exif data is None (empty) load new empty dictionary
            if not exif_dict:
                exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
            #fill author data            
            if 'people' in jsonData and len(jsonData['people']) > 0 :
                author = jsonData['people'][0]['name']
                exif_dict['0th'][piexif.ImageIFD.Artist] = author
            #set software to be google photos
            exif_dict['0th'][piexif.ImageIFD.Software] = "Google Photos"
            #set photo time
            if 'photoTakenTime' in jsonData and 'timestamp' in jsonData['photoTakenTime']:
                timestamp = jsonData['photoTakenTime']['timestamp']
                dateTime = datetime.datetime.fromtimestamp(int(timestamp))
                exif_dict['0th'][piexif.ImageIFD.DateTime] = dateTime.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dateTime.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dateTime.strftime("%Y:%m:%d %H:%M:%S")
            #set geo data
            if 'geoData' in jsonData and 'latitude' in jsonData['geoData'] and 'longitude' in jsonData['geoData']:
                latitude = jsonData['geoData']['latitude']
                longitude = jsonData['geoData']['longitude']
                #https://stackoverflow.com/a/77056370
                latitude_dms = deg_to_dms(latitude, ["S", "N"])
                longitude_dms = deg_to_dms(longitude, ["W", "E"])
                exif_latitude = dms_to_exif_format(latitude_dms[0], latitude_dms[1], latitude_dms[2])
                exif_longitude = dms_to_exif_format(longitude_dms[0], longitude_dms[1], longitude_dms[2])
                exif_dict['GPS'][ piexif.GPSIFD.GPSVersionID] = [2, 0, 0, 0]
                exif_dict['GPS'][ piexif.GPSIFD.GPSLatitude] = exif_latitude
                exif_dict['GPS'][ piexif.GPSIFD.GPSLatitudeRef] = latitude_dms[3]
                exif_dict['GPS'][ piexif.GPSIFD.GPSLongitude] = exif_longitude
                exif_dict['GPS'][ piexif.GPSIFD.GPSLongitudeRef] = longitude_dms[3]
            #set lens data 
            if 'googlePhotosOrigin' in jsonData and 'mobileUpload' in jsonData['googlePhotosOrigin'] and 'deviceType' in jsonData['googlePhotosOrigin']['mobileUpload']:
                exif_dict['Exif'][piexif.ExifIFD.LensModel] = jsonData['googlePhotosOrigin']['mobileUpload']['deviceType']
                exif_dict['Exif'][piexif.ExifIFD.LensMake] = jsonData['googlePhotosOrigin']['mobileUpload']['deviceType']
                exif_dict['0th'][piexif.ImageIFD.Make] = jsonData['googlePhotosOrigin']['mobileUpload']['deviceType']
                exif_dict['0th'][piexif.ImageIFD.Model] = jsonData['googlePhotosOrigin']['mobileUpload']['deviceType']
            #get raw exif data
            exif_bytes = piexif.dump(exif_dict)
            #update exif data on picture
            piexif.insert(exif_bytes, os.path.join(rootPath, fileName))
            #we can delete json file now 
            os.remove(filePath)
            print(f"Updated {fileName} with exif data")
            moveFolder = "D:\\takeout-20240104T140745Z-001\\Takeout\\Google Photos\\Everything"
            #shutil.move(filePath, moveFolder)
            #print(f"Moved {fileName} to {moveFolder}")
