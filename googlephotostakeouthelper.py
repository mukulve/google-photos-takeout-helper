import uuid
import piexif
import shutil
import mimetypes
import datetime
import glob
import json
import os
import fractions

# https://stackoverflow.com/a/77056370
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
# https://stackoverflow.com/a/77056370
def dms_to_exif_format(dms_degrees, dms_minutes, dms_seconds):
    exif_format = (
        (dms_degrees, 1),
        (dms_minutes, 1),
        (int(dms_seconds.limit_denominator(100).numerator), int(dms_seconds.limit_denominator(100).denominator)),
    )
    return exif_format

def getExifDictionary(fileName, rootPath):
    try:
        exif_dict = piexif.load(os.path.join(rootPath, fileName))
    except:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    return exif_dict

def moveImage(filePath, fileName, rootPath, moveFolder, unique_filename):
    os.remove(filePath)
    if not os.path.exists(moveFolder):
        os.makedirs(moveFolder)
    shutil.move(os.path.join(rootPath, fileName), os.path.join(moveFolder, unique_filename))

def CopyGeoData(deg_to_dms, dms_to_exif_format, jsonData, exif_dict):
    if "geoData" in jsonData and "latitude" in jsonData["geoData"] and "longitude" in jsonData["geoData"]:
        latitude = jsonData["geoData"]["latitude"]
        longitude = jsonData["geoData"]["longitude"]
        # https://stackoverflow.com/a/77056370
        latitude_dms = deg_to_dms(latitude, ["S", "N"])
        longitude_dms = deg_to_dms(longitude, ["W", "E"])
        exif_latitude = dms_to_exif_format(latitude_dms[0], latitude_dms[1], latitude_dms[2])
        exif_longitude = dms_to_exif_format(longitude_dms[0], longitude_dms[1], longitude_dms[2])
        exif_dict["GPS"][piexif.GPSIFD.GPSVersionID] = [2, 0, 0, 0]
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = exif_latitude
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = latitude_dms[3]
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = exif_longitude
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = longitude_dms[3]

def CopyCameraData(jsonData, exif_dict):
    if "googlePhotosOrigin" in jsonData and "mobileUpload" in jsonData["googlePhotosOrigin"] and "deviceType" in jsonData["googlePhotosOrigin"]["mobileUpload"]:
        exif_dict["Exif"][piexif.ExifIFD.LensModel] = jsonData["googlePhotosOrigin"]["mobileUpload"]["deviceType"]
        exif_dict["Exif"][piexif.ExifIFD.LensMake] = jsonData["googlePhotosOrigin"]["mobileUpload"]["deviceType"]
        exif_dict["0th"][piexif.ImageIFD.Make] = jsonData["googlePhotosOrigin"]["mobileUpload"]["deviceType"]
        exif_dict["0th"][piexif.ImageIFD.Model] = jsonData["googlePhotosOrigin"]["mobileUpload"]["deviceType"]

def copyDateData(jsonData, exif_dict):
    if "photoTakenTime" in jsonData and "timestamp" in jsonData["photoTakenTime"]:
        timestamp = jsonData["photoTakenTime"]["timestamp"]
        dateTime = datetime.datetime.fromtimestamp(int(timestamp))
        exif_dict["0th"][piexif.ImageIFD.DateTime] = dateTime.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dateTime.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = dateTime.strftime("%Y:%m:%d %H:%M:%S")

def CopyPeopleData(jsonData, exif_dict):
    if "people" in jsonData and len(jsonData["people"]) > 0:
        author = jsonData["people"][0]["name"]
        exif_dict["0th"][piexif.ImageIFD.Artist] = author
        
def ProcessTakeout(baseFolder:str, moveFolder:str):
    for filePath in glob.iglob(baseFolder + "**/**", recursive=True):
        if filePath.endswith("json"):
            jsonData = None
            fileName = None
            with open(filePath, "r") as f:
                jsonData = json.load(f)

            rootPath = os.path.dirname(filePath)

            if "title" in jsonData:
                fileName = jsonData["title"]
            else:
                continue

            if mimetypes.guess_type(os.path.join(rootPath, fileName))[0].startswith("video"):
                continue

            if fileName in os.listdir(rootPath):
                exif_dict = getExifDictionary(fileName, rootPath)
                exif_dict["0th"][piexif.ImageIFD.Software] = "Google Photos"
                CopyPeopleData(jsonData, exif_dict)
                copyDateData(jsonData, exif_dict)
                CopyGeoData(deg_to_dms, dms_to_exif_format, jsonData, exif_dict)
                CopyCameraData(jsonData, exif_dict)
                exif_bytes = None
                base_name, extension = os.path.splitext(fileName)
                unique_filename = f"{base_name}_{uuid.uuid4()}{extension}"
                try:
                    exif_bytes = piexif.dump(exif_dict)
                    piexif.insert(exif_bytes, os.path.join(rootPath, fileName))
                except:
                    pass
                moveImage(filePath, fileName, rootPath, moveFolder, unique_filename)

if __name__ == "__main__":
    baseFolder = input("Enter Folder Containing Takout : ")
    moveFolder = input("Enter Folder To Move Files To : ")
    ProcessTakeout(baseFolder, moveFolder)
