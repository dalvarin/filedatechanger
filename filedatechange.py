#this program takes the name of a file, extracts date and time and sets the modification date and time for the file

import os
import sys
import datetime
import json
import re
from PIL import Image
from PIL.ExifTags import TAGS

from logger.logger_manager import Logger
#import exif

logger = Logger("FDCHANG")
logger_notime = Logger("NOTIMES", show_date=False) # shows commands output

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    if info is not None:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
    else:
        logger.info(f"File '{fn}' has no EXIF data.")
    return ret


# this function gets all the files in the current directory
def get_files_in_directory(directory):
    # List to store file names
    files = []

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        # Construct full path
        full_path = os.path.join(directory, item)
        # Check if it's a file
        if os.path.isfile(full_path):
            files.append(item)

    return files

# this function gets the date and time from the file name
def get_date_from_filename(full_path: str, filename: str) -> str:
    """
    Extracts the date and time part from the filename.

    Args:
        filename (str): The name of the file in the format 'filename_YYYYMMDD_HHMMSS.ext'.

    Returns:
        str: The extracted date and time as a string.
    """
    # if the file is a jpg file, try to extract the date from the EXIF data
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        logger.info(f"File '{filename}' is a jpg file.")
        # check if the file exists
        if not os.path.isfile(full_path):
            logger.warning(f"File '{full_path}' does not exist.")
            return None
        # check if the file is empty
        if os.path.getsize(full_path) == 0:
            logger.info(f"File '{full_path}' is empty.")
            return None
        # check if the file is a valid image
        # try:
        #     img = Image.open(full_path)
        #     img.verify()
        # except Exception as e:
        #     print(f"File '{full_path}' is not a valid image. Error: {e}")
        #     return None
        # try to extract the date from EXIF data using exifreader
        json_data = get_exif(full_path)
        logger.info(f"EXIF data: {json_data}")

        # data = exif.parse(full_path)
        # print (f"EXIF data: {data}")

        if 'DateTimeOriginal' in json_data:
            # Convert the date string to a datetime object
            dt = datetime.datetime.strptime(json_data['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
            # Convert the datetime object to a string in the desired format
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            # Return the formatted date string
            return dt
        elif 'DateTimeDigitized' in json_data:
            # Convert the date string to a datetime object
            dt = datetime.datetime.strptime(json_data['DateTimeDigitized'], "%Y:%m:%d %H:%M:%S")
            # Convert the datetime object to a string in the desired format
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            # Return the formatted date string
            return dt
        elif 'DateTime' in json_data:
            # Convert the date string to a datetime object
            dt = datetime.datetime.strptime(json_data['DateTime'], "%Y:%m:%d %H:%M:%S")
            # Convert the datetime object to a string in the desired format
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            # Return the formatted date string
            return dt
        else:
            logger.warning(f"File '{filename}' has no valid date and time EXIF data.")

    # if fullpath.json exists, read the date from it
    if os.path.isfile(full_path + '.json'):
        logger.info(f"File '{full_path}.json' exists.")
        with open(full_path + '.json', 'r') as f:
            # get json data from the file
            data = f.read()
            # get photoTakenTime field from json data
            json_data = json.loads(data)
            # check if the field exists
            if 'photoTakenTime' in json_data:
                logger.info (f"File '{full_path}.json' has 'photoTakenTime' field.")
                # get the date and time from the field
                dt = json_data['photoTakenTime']
                # convert the date and time to a datetime object
                dt = datetime.datetime.fromtimestamp(int(dt['timestamp']))
                # convert the datetime object to a string in the desired format
                dt = dt.strftime("%Y-%m-%d %H:%M:%S")
                # return the formatted date string
                return dt
            else:
                logger.warning(f"File '{full_path}.json' has no valid date and time EXIF data.")

    # if the file name matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*.jpg'
    if re.match(r'IMG-\d{8}-WA\d+\.jpg', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*.jpg'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return date_str
    
    # if the file name matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*\.*.jpg'
    if re.match(r'IMG-\d{8}-WA\d+\.*.*\.jpg', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*\.*.jpg'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return date_str

    # if the file name matchs the regex pattern 'YYYY-MM-DD HH.MM.SS.*.jpg'
    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}.*\.jpg', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'YYYY-MM-DD HH.MM.SS.*.jpg'")
        year = filename.split('-')[0]
        month = filename.split('-')[1]
        day = filename.split('-')[2].split(' ')[0]
        hour = filename.split(' ')[1].split('.')[0]
        minute = filename.split('.')[1]
        second = filename.split('.')[2].split('.')[0]
        date_str = f'{year}-{month}-{day} {hour}:{minute}:{second}'
        return date_str
    
    # if the file name matchs the regex pattern 'YYYYMMDD_HHMMSS.*'
    if re.match(r'\d{8}_\d{6}.*', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'YYYYMMDD_HHMMSS.*'")
        year = filename.split('_')[0][:4]
        month = filename.split('_')[0][4:6]
        day = filename.split('_')[0][6:]
        hour = filename.split('_')[1][:2]
        minute = filename.split('_')[1][2:4]
        second = filename.split('_')[1][4:6]
        date_str = f'{year}-{month}-{day} {hour}:{minute}:{second}'
        return date_str
    
    # if the file name matchs the regex pattern 'VID-YYYYMMDD-\.*.*'
    if re.match(r'VID-\d{8}-\.*.*', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'VID-YYYYMMDD-\.*.*'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return date_str
    
    # if the file name matchs the regex pattern 'Screenshot_YYYYMMDD-HHMMSS\.*.*'
    if re.match(r'Screenshot_\d{8}-\d{6}.*', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'Screenshot_YYYYMMDD-HHMMSS\.*.*'")
        year = filename.split('_')[1][:4]
        month = filename.split('_')[1][4:6]
        day = filename.split('_')[1][6:8]
        hour = filename.split('-')[1][:2]
        minute = filename.split('-')[1][2:4]
        second = filename.split('-')[1][4:6]
        date_str = f'{year}-{month}-{day} {hour}:{minute}:{second}'
        return date_str

    logger.warning(f"File '{filename}' does not match any known date format.")
    return None


def set_file_date(file_path: str, date_str: str) -> None:
    """
    Sets the modification date and time of a file.

    Args:
        file_path (str): The path to the file.
        date_str (str): The date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        None
    """
    try:
        # Convert the date string to a datetime object
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # Convert the datetime object to a timestamp
        timestamp = dt.timestamp()

        # Set the file's modification time
        os.utime(file_path, (timestamp, timestamp))
    except Exception as e:
        logger.error(f"Error setting date for file '{file_path}': {e}")
        return

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        logger.info("Usage: python filedatechange.py <file_path>")
        sys.exit(1)

    # Get the file path and date string from command line arguments
    file_path = sys.argv[1]

    # check if the file path is a directory
    if os.path.isdir(file_path):
        # Get all files in the directory
        logger.info(f"'{file_path}' is a directory.")
        files = get_files_in_directory(file_path)
        #print(f"Files in directory '{file_path}': {files}")
        # Set the modification date for each file
        for file in files:
            if file.endswith('.json'):
                logger.info(f"Skipping json file: {file}")
                continue
            # if filename is Thumbs.db, skip it
            if file == 'Thumbs.db':
                logger.info(f"Skipping Thumbs.db file: {file}")
                continue
            # check if the file is a directory

            if os.path.isdir(os.path.join(file_path, file)):
                logger.info(f"Skipping directory: {file}")
                continue
            logger.info(f"Setting date for file: {file}")
            full_path = os.path.join(file_path, file)
            date_str = get_date_from_filename(full_path,file)
            if date_str is None:
                logger.warning(f"Could not extract date from file '{file}'. Skipping...")
                continue
            logger.info(f"Extracted date string: {date_str}")
            set_file_date(full_path, date_str)
        sys.exit(0)

    # Check if the file exists
    if not os.path.isfile(file_path):
        logger.warning(f"File '{file_path}' does not exist.")
        sys.exit(1)

    # Get the file date from the filename
    date_str = get_date_from_filename(file_path,os.path.basename(file_path))
    if date_str is None:
        logger.error(f"Could not extract date from file '{file_path}'.")
        sys.exit(1)
    logger.info(f"Extracted date string: {date_str}")

    # Set the file's modification date
    set_file_date(file_path, date_str)

