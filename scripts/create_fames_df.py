import os
import glob
import pandas as pd
import shutil
from datetime import timedelta

camera='ffc'
date='20220731'
letter=['a','b','c','d','e','f','g','h','j','k']
root_folder = '/gws/ssde/j25a/dcmex/users/hburns/DCMEX2/NEW/pass_frames'
output_folder = glob.glob('../frames/*/'+date+'/' + camera +'/*.png')
cloud_passes = pd.read_csv('input_data/FAAM_cloudpass_info.csv')


def create_dataframe_from_images(output_folder):
    # Get a list of all saved image files in the output folder
    #image_files = [file for file in output_folder]
    #Extract information from the image filenames
    data = []
    for image_file in output_folder:
        filename_parts = image_file.split('_')
        print(filename_parts)
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
frame_times = create_dataframe_from_images(output_folder)


# Create a list to store the subsetted DataFrames
pass_dfs = []
pass_no = 0

# Iterate over rows in c305_passes
for index, row in cloud_passes.iterrows():
    start_datetime = pd.to_datetime(row['start_datetime'])
    end_datetime = pd.to_datetime(row['end_datetime'])

    # Subset frame_times based on the datetime range
    subset_df = frame_times[(frame_times['timestamp'] >= start_datetime) & (frame_times['timestamp'] <= end_datetime)].copy()
    
    # Append the subsetted DataFrame to the list with a name like "pass1", "pass2", ...
    pass_name = f"pass_{pass_no + 1:02}"
    pass_no+=1
    
    if row['npasses'] == 1.0:
        if camera=='ffc':
            # Create subset from 30 seconds before start_datetime to start_datetime with 'direction' column set to 'in'
            subset_pass = frame_times[(frame_times['timestamp'] >= (start_datetime - timedelta(seconds=30))) & (frame_times['timestamp'] <= (start_datetime ))].copy()
            subset_pass['direction'] = 'in'
            subset_pass['pass_name'] = pass_name
            subset_pass['start_time'] = start_datetime
        elif camera=='rfc':
            # Create subset from end_datetime to 30 seconds afterwards with 'direction' column set to 'out'
            subset_pass = frame_times[(frame_times['timestamp'] >= (end_datetime - timedelta(seconds=2))) & (frame_times['timestamp'] <= (end_datetime + timedelta(seconds=30)))].copy()
            subset_pass['direction'] = 'out'
            subset_pass['pass_name'] = pass_name
            subset_pass['start_time'] =  end_datetime
        # Append both subsetted DataFrames to the list
        #pass_dfs.append(subset_in)
        pass_dfs.append(subset_pass)

    elif row['npasses'] > 1.0:
        starttimes = row['passes_start_index']
        starttimes = starttimes.strip('[]')
        starttimes = starttimes.split()
        endtimes = row['passes_end_index']
        endtimes = endtimes.strip('[]')
        endtimes = endtimes.split()
        for subpass in range(int(row['npasses'])):
            starttime = start_datetime+timedelta(seconds=(int(starttimes[subpass])-int(row['start_index'])))
            endtime = end_datetime+timedelta(seconds=(int(endtimes[subpass])-int(row['end_index'])))
            if camera=='ffc':
                # Create subset from 30 seconds before start_datetime to start_datetime with 'direction' column set to 'in'
                subset_pass = frame_times[(frame_times['timestamp'] >= (starttime - timedelta(seconds=40))) & (frame_times['timestamp'] <= (starttime))].copy()
                subset_pass['direction'] = 'in'
                subset_pass['pass_name'] = pass_name + '_'+ letter[subpass]
                subset_pass['start_time'] = starttime
            elif camera=='rfc':
                # Create subset from end_datetime to 30 seconds afterwards with 'direction' column set to 'out'
                subset_pass = frame_times[(frame_times['timestamp'] >= endtime - timedelta(seconds=2) ) & (frame_times['timestamp'] <= (endtime + timedelta(seconds=30)))].copy()
                subset_pass['direction'] = 'out'
                subset_pass['pass_name'] = pass_name + '_'+ letter[subpass]
                subset_pass['start_time'] =  endtime
            pass_dfs.append(subset_pass)  
   
    

# Concatenate the list of DataFrames into a single DataFrame
result_df = pd.concat(pass_dfs, ignore_index=True)



# Iterate over rows in result_df
for index, row in result_df.iterrows():

    pass_name = row['pass_name']
    timestamp = row['timestamp']
    direction = row['direction']
    time_label = row['start_time']
    print(timestamp.strftime("%Y%m%d"))
    # Create folder structure
    folder_path = os.path.join(root_folder, timestamp.strftime("%Y%m%d"), str(pass_name)+'_'+time_label.strftime("%H%M%S")+'_'+camera)

    # Create folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    filename_parts = row['filename'].split('/')

    fname=filename_parts[-1]
    print(fname)
    # Copy file to the new folder
    src_file_path = os.path.join('../frames', row['flight_id'],timestamp.strftime("%Y%m%d"),camera, fname) 
    dst_file_path = os.path.join(folder_path, fname)
    shutil.copy(src_file_path, dst_file_path)

# Display the folder structure
print(f"Folder structure created in: {root_folder}")
