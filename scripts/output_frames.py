import glob
import cv2
from datetime import datetime
from datetime import timedelta
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser(description="Process command-line arguments.")
parser.add_argument("--date_to_use", type=int, required=True, help="Date in YYYYMMDD format")
parser.add_argument("--ffc", action="store_true", help="Enable FFC mode")
parser.add_argument("--rfc", action="store_true", help="Enable RFC mode")

args = parser.parse_args()
date=args.date_to_use
if args.ffc:
   camera='ffc'

if args.rfc:
   camera='rfc'
# Read the CSV
df = pd.read_csv('input_data/lag_times.csv')
# Make sure 'date' is treated as string (or int)
df['date'] = df['date'].astype(str)
lag_time = int(df.loc[df['date'] == str(date), 'lag'].values[0])   
print('lag vaulue ',lag_time) 

def extract_frames(input_video_path, output_folder, shift=0):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)

    # Check if the video is opened successfully
    if not cap.isOpened():
        print("Error opening video file.")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Extract timestamp and FlightID from the filename
    filename_parts = input_video_path.split('_')
    date_part = filename_parts[2]
    time_part = filename_parts[5]
    flight_id = filename_parts[4]
    # Create the output folder if it doesn't exist
    print(flight_id+' : '+date_part)
    output_folder = os.path.join(output_folder, flight_id, date_part, camera)
    os.makedirs(output_folder, exist_ok=True)

    # Read and save each frame
    frame_count = 0
    while True:
        ret, frame = cap.read()

        # Break the loop if the video has ended
        if not ret:
            break

        # Get the current timestamp based on the starting time of the recording
        start_time = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
        current_time = start_time + pd.to_timedelta(frame_count / fps, unit='s') + timedelta(seconds=shift)
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")

        # Save the frame as an image with timestamp and FlightID in the filename
        frame_filename = os.path.join(output_folder, f"frame_{flight_id}_{timestamp}.png")
        cv2.imwrite(frame_filename, frame)

        # Display frame count for progress
        print(f"Frame {frame_count} saved with timestamp {timestamp}.")

        frame_count += 1

    # Release the video capture object
    cap.release()

    print("Frames extraction completed.")

#video_paths = glob.glob('faam-video/faam-video-'+camera+'*.mp4')
video_paths = glob.glob('../faam-video/faam-video-'+camera+'*'+str(date)+'*_clean*.mp4')
#print('faam-video/faam-video-'+camera+'_faam_'+date+'_r0_'+flight+'_*.mp4')
output_folder = '../frames'
for video_path in video_paths:
    extract_frames(video_path, output_folder, shift=lag_time)
