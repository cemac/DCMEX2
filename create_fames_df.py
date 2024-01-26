import os
import pandas as pd
import shutil

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

# Create a list to store the subsetted DataFrames
pass_dfs = []
pass_no = 0

# Iterate over rows in c305_passes
for index, row in c305_passes.iterrows():
    start_datetime = pd.to_datetime(row['start_datetime'])
    end_datetime = pd.to_datetime(row['end_datetime'])

    # Subset frame_times based on the datetime range
    subset_df = frame_times[(frame_times['timestamp'] >= start_datetime) & (frame_times['timestamp'] <= end_datetime)].copy()
    
    # Append the subsetted DataFrame to the list with a name like "pass1", "pass2", ...
    pass_name = f"pass_{pass_no + 1}"
    pass_no+=1
    subset_df['pass_name'] = pass_name
    pass_dfs.append(subset_df)

# Concatenate the list of DataFrames into a single DataFrame
result_df = pd.concat(pass_dfs, ignore_index=True)

root_folder = '/localhome/home/earhbu/WORK/DCMEX2'


# Iterate over rows in result_df
for index, row in result_df.iterrows():
    pass_name = row['pass_name']
    timestamp = row['timestamp']

    # Create folder structure
    folder_path = os.path.join(root_folder, timestamp.strftime("%Y%m%d"), pass_name)

    # Create folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Copy file to the new folder
    src_file_path = os.path.join('output_frames', row['flight_id'], row['filename'])
    dst_file_path = os.path.join(folder_path, row['filename'])
    shutil.copy(src_file_path, dst_file_path)

# Display the folder structure
print(f"Folder structure created in: {root_folder}")