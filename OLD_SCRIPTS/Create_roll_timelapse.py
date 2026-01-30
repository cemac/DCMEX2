import os
import glob
import pandas as pd
import shutil
from datetime import timedelta

camera='rfc'
letter=['a','b','c','d','e','f','g','h','j','k']

def create_dataframe_from_images(output_folder):
    # Get a list of all saved image files in the output folder
    #image_files = [file for file in output_folder]
    #Extract information from the image filenames
    data = []
    for image_file in output_folder:
        filename_parts = image_file.split('_')
        flight_id = filename_parts[2]
        date = filename_parts[3]
        times = filename_parts[4][0:-4]
        # Convert timestamp to full datetime format
        full_timestamp = pd.to_datetime(date+'_'+times, format="%Y%m%d_%H%M%S")
        data.append({
            'filename': image_file,
            'flight_id': flight_id,
            'timestamp': full_timestamp
        })

    # Create a DataFrame from the extracted information
    df = pd.DataFrame(data)
    df = df.sort_values(by='timestamp').reset_index(drop=True)

    return df