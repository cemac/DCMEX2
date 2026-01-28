import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd
import math
from datetime import datetime
from PIL import Image
from skimage import color
from skimage import io
import cv2
import sys
import glob
import os
from pathlib import Path
home = Path.home()
import pandas as pd
from datetime import timedelta
import argparse
module_dir = "/gws/ssde/j25a/dcmex/users/hburns/DCMEX2/"
if module_dir not in sys.path:
    sys.path.append(module_dir)
import height_calculator as hc
# dummy file name
file_name_full = '/gws/ssde/j25a/dcmex/users/hburns/DCMEX2/cloud_heights/images/20220723/pass_271_ffc/frame_c307_20220730_162917_sky_bluesky_ffc.png'
# set the camera name this chages the edge detection settings, and pitch correction

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Process some inputs.')

# Define the command-line arguments
parser.add_argument('--file', type=str, required=True, help='Full file name')
parser.add_argument('--py', type=int, required=True, default=0, help='Y pixel value')
parser.add_argument('--D', type=int, required=True, help='Distance value')
parser.add_argument('--px', type=int, required=True, help='X pixel value')

# Parse the arguments
args = parser.parse_args()

# Assign the parsed arguments to variables
file_name_full = args.file
pixel_height_override = False
distance_override = False
x_target_override = False
if args.py is not None:
    yo = args.py
    pixel_height_override = True
    print(f'y pixel point h: {yo}')

if args.D is not None:
    D3 = args.D
    distance_override = True
    print(f'Distance h : {D3}')

if args.px is not None:    
    x_target = args.px
    print(f'x pixel point h: {x_target}')
    x_target_override = True


# Print the values to verify
print(f'file_name_full: {file_name_full}')
base_folder="/gws/ssde/j25a/dcmex/users/hburns/DCMEX2/NEW/"
BASE_DIR = Path(base_folder).resolve()
file_path = Path(file_name_full).resolve()
if not file_path.is_relative_to(BASE_DIR):
        print(f"Error: File {file_path} is not inside {BASE_DIR}")
        sys.exit(1)


# Define a function to find the closest roll_time and get the corresponding roll_angle
def get_closest_roll_angle(aircraft_df, frame_time):
    """
    Returns the roll angle from the aircraft DataFrame that is closest to the given frame time.

    Parameters:
    - aircraft_df (pandas.DataFrame): DataFrame containing roll angles and corresponding times.
    - frame_time (float): Time value for which the closest roll angle is to be found.

    Returns:
    - float: The roll angle that is closest to the given frame time.
    """
    # Calculate the absolute difference between frame_time and all roll_times
    diffs = abs(aircraft_df['times'] - frame_time)
    # Find the index of the minimum difference
    min_diff_index = diffs.idxmin()
    # Return the corresponding roll_angle
    return aircraft_df.loc[min_diff_index]

def extract_variables(dataset):
    """
    Extracts variables from the given dataset and returns a pandas DataFrame.

    Parameters:
    - dataset: The dataset containing the required variables.

    Returns:
    - aircraft_df: A pandas DataFrame containing the extracted variables.

    """
    roll = dataset['ROLL_GIN']
    lat = dataset['LAT_GIN'].data[:]
    lon = dataset['LON_GIN'].data[:]
    pitch = dataset['PTCH_GIN'].data[:]
    alt = dataset['ALT_GIN'].data[:]
    veln = dataset['VELN_GIN'].data[:]
    vele = dataset['VELE_GIN'].data[:]
    roll_times = roll.Time
    roll_angle = roll.data[:]
    roll_times_pd = pd.to_datetime(roll_times.data)
    aircraft_df = pd.DataFrame({'times': roll_times_pd, 'lat': lat, 'lon' : lon, 'pitch' : pitch, 'alt': alt, 
                                'roll_angles': roll_angle, 'veln': veln, 'vele': vele})
    return aircraft_df

alphabet_to_numbers = {chr(i): i - 97 for i in range(97, 123)}



# Define the column names
columns = ['Distance', 'plane_height', 'pass_height', 'cloud_height', 'cloud_above_plane_height',
           'roll', 'pitch', 'pixel height', 'x_target','pass_number', 'camera', 'timestamp']

# Create an empty DataFrame with the specified columns
df = pd.DataFrame(columns=columns)

# Get the distance
#extract info
filepath_parts = file_name_full.split('/')
print(filepath_parts)
filename_parts = filepath_parts[-1].split('_')
camera = filepath_parts[-2].split('_')[-1]
date = filename_parts[2]
times = filename_parts[3]
print(date,times)
try:
    full_timestamp = pd.to_datetime(date + '_' + times, format="%Y%m%d_%H%M%S")
except:
    times = os.path.splitext(times)[0]
    full_timestamp = pd.to_datetime(date + '_' + times, format="%Y%m%d_%H%M%S")

if camera == 'ffc': 
    ffc = True
    rfc = False
if camera == 'rfc':
    rfc = True
    ffc = False
dataset = xr.open_dataset(glob.glob('/badc/faam/data/2022/*/core_processed/core_faam_'+date+'_v005_r0_*_1hz.nc')[0])
print(camera)
print(base_folder+'frames/*/*/'+camera+'/frame_c*_'+date+'_'+times+'*.png')
image_file = glob.glob(base_folder+'frames//*/*/'+camera+'/frame_c*_'+date+'_'+times+'*.png')[0]
print('Date and Time: ', date+' '+times)
print('Processing: ', filepath_parts[-1])
print('Cammera: ',camera)
aircraft_df = extract_variables(dataset)
aircraft_position = get_closest_roll_angle(aircraft_df, full_timestamp)

# Check roll
if abs(aircraft_position['roll_angles']) > 15:
    print('Aircraft not level')
    print(aircraft_position['roll_angles'])
    print(aircraft_position['roll_angles'])

        


D = D3
 


pixel_height = 576-yo
print('Overriding pixel height to: ', yo)


pixel_height_adj=pixel_height-576/2
print('Pixel height above center: ', pixel_height_adj)
print('pitch now: ',aircraft_position['pitch'])

if ffc:
    calculator1=hc.CloudHeightCalculator(pixel_height_adj,D,aircraft_position['pitch']-3)
    
if rfc:
    calculator1=hc.CloudHeightCalculator(pixel_height_adj,D,-aircraft_position['pitch']+3)
   
height_corrected1 =calculator1.calculate_height()



# correct height of center of frame 
if ffc:
    x1=D*math.tan(math.radians(aircraft_position['pitch']-3))
   
if rfc:
    x1=D*math.tan(math.radians(-aircraft_position['pitch']+3))
    



# cloud top height is height of cloud edge + aircraft height 
# + height adjustment of the center of the frame
if ffc:    
    cloud_top_height1 = height_corrected1 + aircraft_position['alt']+x1
   
if rfc: 
    cloud_top_height1 = height_corrected1 + aircraft_position['alt']+x1
    

print('the estimated cloud top height is: ', cloud_top_height1)
print('the aircraft height is: ', aircraft_position['alt'])


img = io.imread(image_file)
fig, ax = plt.subplots(figsize=(14, 10))
plt.imshow(img)
try:
    plt.plot(x_target, 576-pixel_height, 'ro')
    
    # Add text at the red dot position
    plt.text(150, 576 - pixel_height+30, f'D: {int(D)}m, CTH: {int(cloud_top_height1)} m', color='k', fontsize=12, ha='left', va='bottom')
    plt.text(300, 480, f'aircraft height: {int(aircraft_position["alt"])} m', color='k', fontsize=12, ha='left', va='bottom')
    
    # Display the roll_angle
    plt.text(0.1, 0.5, f'{aircraft_position['roll_angles']:,.2f}',
                color='red',
                horizontalalignment='left',
                verticalalignment='center',
                transform = plt.gca().transAxes,alpha=0.4)
    # Add a custom legend with just text
    legend_text = "Legend:\n D  = Distance\n CTH = Cloud Top Height\n APH = Aircraft Pass Height"

    # Position the text at the desired location
    plt.text(730, 16, legend_text, fontsize=10, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
   
except ValueError:
    print('skipping')
   
# Calculate line coordinates for roll angle
if camera == 'ffc':
    angle_rad = np.deg2rad(-aircraft_position['roll_angles'])
else:
    angle_rad = np.deg2rad(aircraft_position['roll_angles'])
line_length = img.shape[1] / 2
x = [img.shape[1] / 2 - line_length * np.cos(angle_rad), img.shape[1] / 2 + line_length * np.cos(angle_rad)]
y = [img.shape[0] / 2 - line_length * np.sin(angle_rad), img.shape[0] / 2 + line_length * np.sin(angle_rad)]

# Plot line
plt.plot(x, y, color='red',linestyle='dashed',alpha=0.3)
plt.title('Manual cloud height estimate for '+date, fontsize=20)



plt.savefig('{}_{}_{}.png'.format(date,times,camera),
                    bbox_inches='tight', pad_inches=0.5)
print('saving to: ', '{}_{}_{}.png'.format(date,times,camera))



df.at[0,'Distance'] = D
df.at[0,'plane_height'] = aircraft_position['alt']
df.at[0,'cloud_height'] = cloud_top_height1
df.at[0,'roll'] = aircraft_position['roll_angles']
df.at[0,'pitch'] = aircraft_position['pitch']    
df.at[0,'pixel_height'] = pixel_height
df.at[0,'x_target'] = x_target
df.at[0,'camera'] = camera
df.at[0,'timestamp'] = full_timestamp

try:
    df.to_csv('cloud_heights_'+date+times+'.csv')
    print('saving to: ', 'cloud_heights_'+date+times+'.csv')
except:
    df.to_csv(home+'cloud_heights_'+date+times+'.csv')
    print('saving to: ', home+'cloud_heights_'+date+times+'.csv')

plt.show()
plt.cla()
