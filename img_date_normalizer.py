import os
import sys
import argparse
import re
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from piexif import ExifIFD, load, dump, insert
import enlighten

from logger.logger_manager import Logger

logger = Logger("MODDATE")
logger_notime = Logger("NOTIMES", show_date=False) # shows commands output

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

def get_modification_date(file_path):
    """Get the modification date of a file."""
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)

def set_exif_date(file_path, mod_date):
    """Set the EXIF DateTimeOriginal tag to the modification date."""
    try:
        with Image.open(file_path) as img:
            exif_data = img.info.get('exif', b'')
            # Check if the image has EXIF data. if not, create a new one
            if not exif_data:
                # Create a new EXIF data structure
                # This is a placeholder; you may need to create a proper EXIF structure
                # depending on the image format and requirements.
                # For example, you can use piexif to create a new EXIF structure
                logger.warning(f"No EXIF data found in {file_path}. Creating new EXIF data.")
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}
            else:
                # Update EXIF data
                exif_dict = load(exif_data)
                
            # Convert modification date to EXIF format
            exif_date = mod_date.strftime("%Y:%m:%d %H:%M:%S")

            exif_dict["Exif"][ExifIFD.DateTimeOriginal] = exif_date.encode('utf-8')
            exif_dict["Exif"][ExifIFD.DateTimeDigitized] = exif_date.encode('utf-8')

            # Save the updated EXIF data back to the image
            exif_bytes = dump(exif_dict)
            insert(exif_bytes, file_path)
            logger.info(f"EXIF DateTimeOriginal and DateTimeDigitized updated to {exif_date} for {file_path}")
    except Exception as e:
        logger.error(f"Error updating EXIF data: {e}")

def get_exif_date(file_path):
    """Get the EXIF DateTimeOriginal tag from an image."""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                logger.info(f"No EXIF data found in {file_path}.")
                return None
            for tag, value in exif_data.items():
                if TAGS.get(tag) == 'DateTimeOriginal':
                    # Convert the EXIF date to a datetime object
                    exif_date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return exif_date
    except Exception as e:
        logger.error(f"Error reading EXIF data: {e}")
        return None
    
def get_filename_date(file_path):
    # if the file name matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*.jpg'
    filename = os.path.basename(file_path)
    if re.match(r'IMG-\d{8}-WA\d+\.jpg', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*.jpg'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # if the file name matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*\.*.jpg'
    if re.match(r'IMG-\d{8}-WA\d+\.*.*\.jpg', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*\.*.jpg'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

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
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
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
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # if the file name matchs the regex pattern 'VID-YYYYMMDD-\.*.*'
    if re.match(r'VID-\d{8}-\.*.*', filename):
        # extract the date from the file name
        logger.info(f"File '{filename}' matchs the regex pattern 'VID-YYYYMMDD-\.*.*'")
        year = filename.split('-')[1][:4]
        month = filename.split('-')[1][4:6]
        day = filename.split('-')[1][6:]
        date_str = f'{year}-{month}-{day} 00:00:00'
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
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
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    logger.warning(f"File '{filename}' does not match any known date format.")
    return None

def get_json_date(file_path):
    """Get the date from the associated JSON file."""
    if os.path.isfile(file_path + '.json'):
        logger.info(f"File '{file_path}.json' exists.")
        with open(file_path + '.json', 'r') as f:
            # get json data from the file
            data = f.read()
            # get photoTakenTime field from json data
            json_data = json.loads(data)
            # check if the field exists
            if 'photoTakenTime' in json_data:
                logger.info (f"File '{file_path}.json' has 'photoTakenTime' field.")
                # get the date and time from the field
                dt = json_data['photoTakenTime']
                # convert the date and time to a datetime object
                dt = datetime.fromtimestamp(int(dt['timestamp']))
                return dt
            else:
                logger.warning(f"File '{file_path}.json' has no valid date and time EXIF data.")
    else:
        logger.warning(f"File '{file_path}.json' does not exist.")
        return None

def process_file(file_path: str, provided_date: datetime, force_json_date: bool, force_filename_date: bool, force_mod_date: bool) -> None:
    """Process a file to set its EXIF date and file date."""
    if not file_path.endswith('.jpg') and not file_path.endswith('.jpeg'):
        logger.info(f"Skipping non-JPG file: {file_path}")
        return
    
    if provided_date:
        taken_date = provided_date
        set_exif_date(file_path, taken_date)
        set_file_date(file_path, taken_date)
        return
    elif force_json_date:
        taken_date = get_json_date(file_path)
        if not taken_date:
            taken_date = get_filename_date(file_path)
            if not taken_date:
                logger.info(f"No date found in filename for {file_path}. Using modification date.")
                taken_date = get_modification_date(file_path)
            else:
                logger.info(f"Date found in filename for {file_path}: {taken_date}.")
        else:
            logger.info(f"Date found in JSON file for {file_path}: {taken_date}.")
        set_exif_date(file_path, taken_date)
        set_file_date(file_path, taken_date)
        return
    elif force_filename_date:
        taken_date = get_filename_date(file_path)
        if not taken_date:
            logger.info(f"No date found in filename for {file_path}. Using modification date.")
            taken_date = get_modification_date(file_path)
            logger.info(f"Using modification date for {file_path}: {taken_date}.")
        else:
            logger.info(f"Date found in filename for {file_path}: {taken_date}.")
        set_exif_date(file_path, taken_date)
        set_file_date(file_path, taken_date)
        return
    elif force_mod_date:
        taken_date = get_modification_date(file_path)
        logger.info(f"Using modification date for {file_path}: {taken_date}.")
        set_exif_date(file_path, taken_date)
        set_file_date(file_path, taken_date)
        return

    else:
        taken_date = get_exif_date(file_path)
        if not taken_date:
            logger.info(f"No EXIF date found for {file_path}.")
            taken_date = get_json_date(file_path)
            if not taken_date:
                logger.info(f"No date found in JSON file for {file_path}.")
                taken_date = get_filename_date(file_path)
                if not taken_date:
                    logger.info(f"No date found in filename for {file_path}. Using modification date.")
                    taken_date = get_modification_date(file_path)
                    logger.info(f"Using modification date for {file_path}: {taken_date}.")
                else:
                    logger.info(f"Date found in filename for {file_path}: {taken_date}.")
            else:
                logger.info(f"Date found in JSON file for {file_path}: {taken_date}.")
        else:
            logger.info(f"Date found in EXIF data for {file_path}: {taken_date}.")
        set_exif_date(file_path, taken_date)
        set_file_date(file_path, taken_date)
        return
        
def set_file_date(file_path: str, datetime: datetime) -> None:
    """
    Sets the modification date and time of a file.

    Args:
        file_path (str): The path to the file.
        date_str (str): The date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        None
    """
    try:

        # Convert the datetime object to a timestamp
        timestamp = datetime.timestamp()

        # Set the file's modification time
        os.utime(file_path, (timestamp, timestamp))
        logger.info(f"File modification date set to {datetime} for {file_path}")
    except Exception as e:
        logger.error(f"Error setting date for file '{file_path}': {e}")
        return

def main():
    """Main function to process files or directories."""

    # process command line arguments using argparse
    # argument filename <path_to_jpg_file> it is mandatory
    # argument -d "<date time>"
    # argument -e, use exif date
    # argument -m, use file modification date
    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
    parser.add_argument('path', type=str, help='Path to the JPG file or directory')
    parser.add_argument('-d', '--date', type=str, help='Date and time to set for the file')
    parser.add_argument('-f', '--filenamedate', action='store_true', help='Use date from filename')
    parser.add_argument('-m', '--modificationdate', action='store_true', help='Use file modification date')
    parser.add_argument('-j', '--jsondate', action='store_true', help='Use date from associated JSON file')

    # parse the arguments
    args = parser.parse_args()
    # check if the filename argument is provided
    if not args.path:
        logger.error("Filename or directory name argument is required.")
        sys.exit(1)
    # check if the file exists
    if not os.path.exists(args.path):
        logger.error(f"File not found: {args.path}")
        sys.exit(1) 

    # if the date argument is provided, set the date
    provided_date = None
    if args.date:
        try:
            # parse the date string to datetime object
            provided_date = datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S")
            logger.info(f"Date provided: {provided_date}. It is going to be used for all files.")
            args.jsondate = False
            args.filenamedate = False
            args.modificationdate = False
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            sys.exit(1)

    if args.jsondate:
        logger.info("Forcing the use of date from JSON file.")
        args.filenamedate = False
        args.modificationdate = False

    if args.filenamedate:
        logger.info("Forcing the use of date from filename.")
        args.modificationdate = False

    if args.modificationdate:
        logger.info("Forcing the use of file modification date.")


    # check if the file is a directory
    if os.path.isdir(args.path):
        # Get all files in the directory
        logger.info(f"'{args.path}' is a directory.")
        files = get_files_in_directory(args.path)
        num_files = len(files)

        manager = enlighten.get_manager()
        status_bar = manager.status_bar('Processing EXIF dates',
                                color='bold_underline_bright_white_on_lightslategray',
                                justify=enlighten.Justify.CENTER)
        std_bar_format = u'{desc}{desc_pad}{percentage:3.0f}%|{bar}| ' + \
                 u'{count:{len_total}d}/{total:d} ' + \
                 u'[{elapsed}<{eta}, {rate:.2f}{unit_pad}{unit}/s]'
        pbar = manager.counter(total=num_files, desc='Progress', unit='files', color='green', bar_format=std_bar_format)

        # Set the modification date for each file
        for file in files:
            #bar.next()
            pbar.update()
            if os.path.isdir(os.path.join(args.path, file)):
                logger.info(f"Skipping directory: {file}")
                continue
            file = os.path.join(args.path, file)
            logger.info(f"Processing file: {file}")

            process_file(file, provided_date , args.jsondate, args.filenamedate, args.modificationdate)
                
        sys.exit(0)

    process_file(args.path, provided_date, args.jsondate, args.filenamedate, args.modificationdate)

if __name__ == "__main__":
    main()