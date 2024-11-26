#!/usr/local/bin/python3
import os
import glob
from pathlib import Path

# Define directory
directory = '/prometheus/snapshots'

# Find all directories and tar.gz files
directories = glob.glob('2*Z-*')
tarballs = glob.glob('*.tar.gz')

# Sort by modification date (most recent first)
directories.sort(key=os.path.getmtime, reverse=True)
tarballs.sort(key=os.path.getmtime, reverse=True)

# Keep only the 5 most recent directories
for directory in directories[5:]:
    try:
        Path(directory).rmdir()
        print(f"Removed directory: {directory}")
    except Exception as e:
        print(f"Error removing directory {directory}: {e}")

# Keep only the most recent tar.gz file 
for tarball in tarballs[1:]:
    try:
        os.remove(tarball)
        print(f"Removed file: {tarball}")
    except Exception as e:
        print(f"Error removing file {tarball}: {e}")
