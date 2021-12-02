# Used to create a backup file for remote storage
# Creates a zip file of each folder in the list folders
# Try/except as make_archive() to mitigate an issue with files with a last modified timestamp previous to 1/1/1980

import shutil
import datetime

# Create Zip files of different folders
folders = []
for folder in folders:
    try:
        shutil.make_archive('backup.'+folder+'.'+datetime.datetime.today().strftime('%Y%m%d'), 'zip', folder)
        print(folder + ' has been zipped')
    except Exception as e:
        print(e)
