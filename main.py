#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3
import subprocess
import sys
import tqdm
import imagehash
import magic
from PIL import Image, ExifTags
from termcolor import cprint

x = open('config.txt', 'r')
r = x.read()
x.close()

subprocess.call("rm -f images_info.db", shell=True)

img_dir = r.split('\n')[0].split(':')[1].strip()


######################################## HASHING ######################################


def get_image_files(path):
    def is_image(file_name):
        # List mime types fully supported by Pillow
        full_supported_formats = ['gif', 'jp2', 'jpeg', 'pcx', 'png', 'tiff', 'x-ms-bmp',
                                  'x-portable-pixmap', 'x-xbitmap']
        try:
            mime = magic.from_file(file_name, mime=True)
            return mime.rsplit('/', 1)[1] in full_supported_formats
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

# [ID,Filename,count]

results_dict = {}

conn = sqlite3.connect('images_info.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS IMAGES(
   ID INTEGER PRIMARY KEY AUTOINCREMENT,
   count           INT      NOT NULL,
   name            TEXT       NOT NULL
)''')

images = list(get_image_files(img_dir))

for i in tqdm.tqdm(range(len(images))):
    image = images[i]
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

for record in sorted_count:
    c.execute("INSERT INTO IMAGES VALUES (NULL, ?, ?)", (record[1], record[0]))

conn.commit()
conn.close()

if len(sys.argv) > 1:
    if sys.argv[1] == "web":
        subprocess.call("python3 web_app/app.py", shell=True)
