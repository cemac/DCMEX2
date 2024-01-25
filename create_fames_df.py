import os
import pandas as pd

def create_dataframe_from_images(output_folder):
    # Get a list of all saved image files in the output folder
    image_files = [file for file in os.listdir(output_folder) if file.endswith('.png')]

    #Extract information from the image filenames
    data = []
    for image_file in image_files:
        filename_parts = image_file.split('_')
        flight_id = filename_parts[1]
        date = filename_parts[2]
        times = filename_parts[3][0:-4]

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

# Create DataFrame of video frames 
output_folder = 'output_frames/c305'
frame_times = create_dataframe_from_images(output_folder)

cloud_passes = pd.read_csv('FAAM_cloudpass_info.csv')
c305_passes = cloud_passes[cloud_passes['flight_id'] == 'c305']