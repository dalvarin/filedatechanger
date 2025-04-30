import os
import sys
import time
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
    if len(sys.argv) != 2:
        logger.warning("Usage: python moddate2exif.py <path_to_jpg_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    if os.path.isdir(file_path):
        # Get all files in the directory
        logger.info(f"'{file_path}' is a directory.")
        files = get_files_in_directory(file_path)
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
            if os.path.isdir(os.path.join(file_path, file)):
                logger.info(f"Skipping directory: {file}")
                continue
            if not file.endswith('.jpg') and not file.endswith('.jpeg'):
                logger.info(f"Skipping non-JPG file: {file}")
                continue
            file = os.path.join(file_path, file)
            logger.info(f"Processing file: {file}")
            mod_date = get_modification_date(file)
            set_exif_date(file, mod_date)
            set_file_date(file, mod_date)
            time.sleep(1)
                
        sys.exit(0)

    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    mod_date = get_modification_date(file_path)
    set_exif_date(file_path, mod_date)
    set_file_date(file_path, mod_date)

if __name__ == "__main__":
    main()