#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import re

# Define range for blue color in HSV
lower_blue = np.array([110,50,50])
upper_blue = np.array([130,255,255])

root_dir = '20220727/'

# Load the images along with their file names
images = [(cv2.imread(file), file) for file in glob.glob(root_dir + '*/*')]

# Convert images to grayscale and apply thresholding
threshold = 200  # Adjust this value as needed
binary_images = [(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), threshold, 255, cv2.THRESH_BINARY)[1], file) for img, file in images]

# Define the key function to extract the date and timestamp from the file name
def get_datetime_from_filename(file):
    """
    Extracts the date and timestamp from the given filename.

    Args:
        file (str): The filename to extract the date and timestamp from.

    Returns:
        int: The combined date and timestamp as an integer.

    Raises:
        None

    """
    match = re.search(r'frame_c305_(\d{8})_(\d{6})', file)
    if match:
        date = match.group(1)
        timestamp = match.group(2)
        return int(date + timestamp)
    else:
        print("No match")
        return 0

# Find the first image with significant sky and rename files
for i, (binary_img, file) in enumerate(binary_images):
    sky_pixels = cv2.countNonZero(binary_img)
    if sky_pixels > threshold and "_sky" not in file:
        new_file_name = os.path.splitext(file)[0] + "_sky" + os.path.splitext(file)[1]
        os.rename(file, new_file_name)
    elif "_allcloud" not in file:
        new_file_name = os.path.splitext(file)[0] + "_allcloud" + os.path.splitext(file)[1]
        os.rename(file, new_file_name)

# Loop through all the directories in root_dir
for dir_name, sub_dirs, files in os.walk(root_dir):
    if dir_name == root_dir:
        continue    
    # Check if the directory contains only files with the "_allcloud" tag
    allcloud_files = glob.glob(os.path.join(dir_name, "*_allcloud.*"))
    if len(files) == len(allcloud_files) and "_allcloud" not in dir_name:
        new_dir_name = dir_name + "_allcloud"
        os.rename(dir_name, new_dir_name)

# Load the images along with their file names
images = [(cv2.imread(file), file) for file in glob.glob(root_dir + '*/*_sky.*')]
dir = '20220727/*/*_sky.*' # Directory containing the images

for img, file in images:
    # Convert the image from BGR to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

     # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Count the number of blue pixels
    blue_pixels = cv2.countNonZero(mask)

    # If the image has more than 20000 blue pixels, rename it to include the "_bluesky" tag
    if blue_pixels > 10000:
        if "_bluesky" not in file:
            new_file_name = os.path.splitext(file)[0] + "_bluesky" + os.path.splitext(file)[1]
            os.rename(file, new_file_name)





# Loop through all the directories in root_dir
for dir_name, sub_dirs, files in os.walk(root_dir):
    subdir_name = os.path.basename(dir_name)
    print(subdir_name)
    # Get all the images in the directory
    image_files = glob.glob(os.path.join(dir_name, "*.png"))  # Adjust the file extension as needed
 
    image_files.sort(key=lambda f: re.search(r'(\d{6})_\w+', f).group(1) if re.search(r'(\d{6})_\w+', f) else '')
    # Sort the image files based on the extracted datetime
    image_files = sorted(image_files, key=get_datetime_from_filename)
   
    # Create a new figure for the directory
    fig = plt.figure(figsize=(10, 10))

    # Calculate the number of rows and columns based on the number of images
    num_images = len(image_files)
    num_rows = (num_images + 4) // 5  # Adjust the grid size as needed
    num_cols = min(num_images, 5)
    
    # Loop through the images and add them to the figure
    for i, file in enumerate(image_files):
        img = mpimg.imread(file)
        
        # If the image name includes the tag "_bluesky", add a green border to the image
        if "_bluesky" in file:
            border_color = (0, 255, 0)  # Green color
            border_width = 20
            img = cv2.copyMakeBorder(img, border_width, border_width, border_width, border_width, cv2.BORDER_CONSTANT, value=border_color)

        ax = fig.add_subplot(num_rows, num_cols, i+1)
        ax.imshow(img)
        ax.axis('off') # save figure
    if num_images > 0:
        fig.suptitle(subdir_name, fontsize=16)
        plt.tight_layout()
        fig.subplots_adjust(top=0.88)
        plt.savefig(root_dir+'/' + subdir_name + '.png')
        plt.close(fig)
    

    

