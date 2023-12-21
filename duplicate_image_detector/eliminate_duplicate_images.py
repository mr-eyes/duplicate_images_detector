#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import tqdm
import imagehash
import magic
import configparser

from PIL import Image, ExifTags
from termcolor import cprint
from db_handler import ImagesDB

######################################## CONSTANTS ######################################
IMG_INFO_DB_FILENAME = "images_info.db"
# List mime types fully supported by Pillow
FULL_SUPPORTED_FORMATS = ['gif', 'jp2', 'jpeg', 'pcx', 'png', 'tiff', 'x-ms-bmp',
                            'x-portable-pixmap', 'x-xbitmap']
######################################## HASHING ######################################


def get_image_files(path):
    def is_image(file_name):
        try:
            mime = magic.from_file(file_name, mime=True)
            return mime.rsplit('/', 1)[1] in FULL_SUPPORTED_FORMATS
        except IndexError:
            return False

    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            file = os.path.join(root, file)
            if is_image(file):
                yield (file)


def get_file_size(file_name):
    try:
        return os.path.getsize(file_name)
    except FileNotFoundError:
        return 0


def get_image_size(img):
    return "{} x {}".format(*img.size)


def get_capture_time(img):
    try:
        exif = {
            ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in ExifTags.TAGS
        }
        return exif["DateTimeOriginal"]
    except:
        return "Time unknown"


def hash_file(file):
    try:
        hashes = []
        img = Image.open(file)

        file_size = get_file_size(file)
        image_size = get_image_size(img)
        capture_time = get_capture_time(img)

        # 0 degree hash
        hashes.append(str(imagehash.phash(img)))

        # 90 degree hash
        img = img.rotate(90, expand=True)
        hashes.append(str(imagehash.phash(img)))

        # 180 degree hash
        img = img.rotate(90, expand=True)
        hashes.append(str(imagehash.phash(img)))

        # 270 degree hash
        img = img.rotate(90, expand=True)
        hashes.append(str(imagehash.phash(img)))

        hashes = ''.join(sorted(hashes))

        # cprint("\tHashed {}".format(file), "blue")
        return {"hash": hashes, "_id": file}
    except OSError:
        cprint("\tUnable to open {}".format(file), "red")
        return 0


######################################## END HASHING ######################################

def read_config():
    """read from configuration file
    """
    config = configparser.ConfigParser()
    if not os.path.exists("config.cfg"):
        raise FileNotFoundError("configuration file (config.cfg) not found!")
    config.read("config.cfg")
    return config

def process():
    """execute the routine of eliminating duplicate images
    """
    config = read_config()
    

    img_dir = config['DEFAULT']['images_directory']
    results_dict = {}
    images = list(get_image_files(img_dir))
    for image in tqdm.tqdm(images):
        info = hash_file(image)
        if info == 0:
            continue

        hash_value = info['hash']

        if hash_value not in results_dict:
            file_name = os.path.basename(info['_id'])
            results_dict[hash_value] = [file_name, 1]
        else:
            results_dict[hash_value][1] += 1

    count = list(results_dict.values())
    sorted_count = sorted(count, key=lambda x: x[1], reverse=True)
    
    with ImagesDB(IMG_INFO_DB_FILENAME) as imgDb:        
        imgDb.insert_batch(sorted_count)

if __name__ == "__main__":
    process()
    if len(sys.argv) > 1:
        if sys.argv[1] == "web":
            from web.app import app
            app.run(1111)
    