#this program takes the name of a file, extracts date and time and sets the modification date and time for the file

import os
import sys
import datetime
import re


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
def get_date_from_filename(filename: str) -> str:
    """
    Extracts the date and time part from the filename.

    Args:
        filename (str): The name of the file in the format 'filename_YYYYMMDD_HHMMSS.ext'.

    Returns:
        str: The extracted date and time as a string.
    """
    # if the file name matchs the regex pattern 'IMG-YYYYMMM-WA[0-9]*.jpg'
    if re.match(r'IMG-\d{8}-WA\d+\.jpg', filename):
       # extract the date from the file name
        date_str = filename.split('-')[1][:4] + '-' + filename.split('-')[1][4:6] + '-' + filename.split('-')[1][6:] + ' ' + filename.split('-')[2].split('.')[0]
        return date_str



def set_file_date(file_path: str, date_str: str) -> None:
    """
    Sets the modification date and time of a file.

    Args:
        file_path (str): The path to the file.
        date_str (str): The date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        None
    """
    # Convert the date string to a datetime object
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # Convert the datetime object to a timestamp
    timestamp = dt.timestamp()

    # Set the file's modification time
    os.utime(file_path, (timestamp, timestamp))

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python filedatechange.py <file_path>")
        sys.exit(1)

    # Get the file path and date string from command line arguments
    file_path = sys.argv[1]

    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        sys.exit(1)

    # Get the file date from the filename
    date_str = get_date_from_filename(os.path.basename(file_path))
    print (f"Extracted date string: {date_str}")

    # Set the file's modification date
    #set_file_date(file_path, date_str)

