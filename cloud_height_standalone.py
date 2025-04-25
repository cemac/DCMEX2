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
module_dir = "/gws/nopw/j04/dcmex/users/hburns/DCMEX2/"
if module_dir not in sys.path:
    sys.path.append(module_dir)
import height_calculator as hc
# dummy file name
file_name_full = '/gws/nopw/j04/dcmex/users/hburns/DCMEX2/cloud_heights/images/20220723/pass_271_ffc/frame_c307_20220730_162917_sky_bluesky_ffc.png'
# set the camera name this chages the edge detection settings, and pitch correction

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Process some inputs.')

# Define the command-line arguments
parser.add_argument('--file', type=str, required=True, help='Full file name')
parser.add_argument('--py', type=int, required=False, default=0, help='Y pixel value')
parser.add_argument('--D', type=int, required=False, help='Distance value')
parser.add_argument('--px', type=int, required=False, help='X pixel value')

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


# Define functions to extract required information 
pass_number = file_name_full.split('/')[-2].split('_')[1]
cloud_passes = pd.read_csv('/gws/nopw/j04/dcmex/users/hburns/DCMEX2/FAAM_cloudpass_info.csv')
# file manipulation functions
def extract_pass_number(file_name):
    """
    Extracts the pass number from a given file name.

    Args:
        file_name (str): The file name to extract the pass number from.

    Returns:
        pass_number (str or list): The pass number extracted from the file name. If the pass number consists of two parts, it will be returned as a list. Otherwise, it will be returned as a string.
    """
    filepath_parts = file_name.split('/')
    if len(filepath_parts[1].split('_')) > 4:
        pass_number = filepath_parts[1].split('_')[1:3]
    else:
        pass_number = filepath_parts[1].split('_')[1]
    return pass_number


def extract_timestamp_from_filename(filepath):
    """
    Extracts the camera and full timestamp from a given filepath.

    Args:
        filepath (str): The path of the file.

    Returns:
        list: A list containing the camera and full timestamp.

    """
    filepath_parts = filepath.split('/')
    filename_parts = filepath_parts[2].split('_')
    if len(filepath_parts[1].split('_')) > 4:
        camera = filepath_parts[1].split('_')[4]
    else:
        camera = filepath_parts[1].split('_')[3]
    date = filename_parts[2]
    times = filename_parts[3]
    full_timestamp = pd.to_datetime(date + '_' + times, format="%Y%m%d_%H%M%S")
    return [camera, full_timestamp]

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
    alt = dataset['PALT_RVS'].data[:]
    veln = dataset['VELN_GIN'].data[:]
    vele = dataset['VELE_GIN'].data[:]
    roll_times = roll.Time
    roll_angle = roll.data[:]
    roll_times_pd = pd.to_datetime(roll_times.data)
    aircraft_df = pd.DataFrame({'times': roll_times_pd, 'lat': lat, 'lon' : lon, 'pitch' : pitch, 'alt': alt, 
                                'roll_angles': roll_angle, 'veln': veln, 'vele': vele})
    return aircraft_df

alphabet_to_numbers = {chr(i): i - 97 for i in range(97, 123)}
def extract_cloud_pass_info(cloud_passes, pass_number, subpass=None):
    """
    Extracts information about a cloud pass based on the pass number and optional subpass.

    Args:
        cloud_passes (pandas.DataFrame): DataFrame containing information about cloud passes.
        pass_number (int): Pass number of the cloud pass.
        subpass (str, optional): Subpass of the cloud pass. Defaults to None.

    Returns:
        list: A list containing the following information:
            - cloud_lat1 (float): Latitude of the starting point of the cloud pass.
            - cloud_lon1 (float): Longitude of the starting point of the cloud pass.
            - cloud_lat2 (float): Latitude of the ending point of the cloud pass.
            - cloud_lon2 (float): Longitude of the ending point of the cloud pass.
            - start_time (datetime): Start time of the cloud pass.
            - end_time (datetime): End time of the cloud pass.
    """
    pass_info = cloud_passes.loc[int(pass_number) - 1]

    cloud_lat1 = pass_info['start_lat']
    cloud_lon1 = pass_info['start_lon']
    cloud_lat2 = pass_info['end_lat']
    cloud_lon2 = pass_info['end_lon']
    if subpass:
        number = alphabet_to_numbers.get(subpass, None)
        start_datetime = pd.to_datetime(pass_info['start_datetime'])
        end_datetime = pd.to_datetime(pass_info['end_datetime'])
        starttimes = pass_info['passes_start_index']
        starttimes = starttimes.strip('[]')
        starttimes = starttimes.split()
        endtimes = pass_info['passes_end_index']
        endtimes = endtimes.strip('[]')
        endtimes = endtimes.split()
        starttime = start_datetime + timedelta(seconds=(int(starttimes[number]) - int(pass_info['start_index'])))
        endtime = end_datetime + timedelta(seconds=(int(endtimes[number]) - int(pass_info['end_index'])))
        start_time = starttime.to_pydatetime()
        end_time = endtime.to_pydatetime()
    else:
        start_time = datetime.strptime(pass_info['start_datetime'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(pass_info['end_datetime'], '%Y-%m-%d %H:%M:%S')
    return [cloud_lat1, cloud_lon1, cloud_lat2, cloud_lon2, start_time, end_time]

def haversine(lon1, lat1, lon2, lat2, alt):
    """
    Calculate the distance between two points on the Earth's surface using the Haversine formula.

    Parameters:
    lon1 (float): The longitude of the first point in degrees.
    lat1 (float): The latitude of the first point in degrees.
    lon2 (float): The longitude of the second point in degrees.
    lat2 (float): The latitude of the second point in degrees.
    alt (float): The altitude in meters.

    Returns:
    float: The distance between the two points in meters.
    """
    R = 6371e3 + alt  # radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = phi2 - phi1

    lambda1 = math.radians(lon1)
    lambda2 = math.radians(lon2)
    dlambda = lambda2 - lambda1

    a = math.sin(dphi / 2) * math.sin(dphi / 2) + math.cos(phi1) * math.cos(phi1) * math.sin(dlambda / 2) * math.sin(dlambda / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = R * c

    return d


# Define the column names
columns = ['Distance', 'plane_height', 'pass_height', 'cloud_height', 'cloud_above_plane_height',
           'roll', 'pitch', 'pixel height', 'x_target','pass_number', 'camera', 'timestamp']

# Create an empty DataFrame with the specified columns
df = pd.DataFrame(columns=columns)

# Get the distance
#extract info
file_name= file_name_full.split('/')[-1]
date=file_name.split('_')[2]
camera_name = file_name.split('_')[-1].split('.')[0]
camera = camera_name 
if camera == 'ffc': 
    ffc = True
    rfc = False
if camera == 'rfc':
    rfc = True
    ffc = False
dataset = xr.open_dataset(glob.glob('/badc/faam/data/2022/*/core_processed/core_faam_'+date+'_v005_r0_*_1hz.nc')[0])
timeframe= file_name.split('_')[3]
timestamp = pd.to_datetime(date+'_'+timeframe, format="%Y%m%d_%H%M%S")
image_file = glob.glob('/gws/nopw/j04/dcmex/users/hburns/DCMEX2/cloud_pass_frames/'+date+'/pass_'+pass_number+'_*_'+camera_name+'/'+file_name.split('.')[0][0:-4]+'.png')[0]
print('Date and Time: ', image_file)
print('Processing: ', file_name)
print('Pass number: ', pass_number)
aircraft_df = extract_variables(dataset)
aircraft_position = get_closest_roll_angle(aircraft_df, timestamp)
if isinstance(pass_number, list):
    pass_info = extract_cloud_pass_info(cloud_passes, pass_number[0], subpass=pass_number[1])
else:
    pass_info = extract_cloud_pass_info(cloud_passes, pass_number)
pass_lat1, pass_lon1, pass_lat2, pass_lon2, start_time, end_time = pass_info
# get mid pass time and thus the aircraft position at that time
mid_pass_time = start_time + (end_time - start_time)/2
aircraft_pass_position = get_closest_roll_angle(aircraft_df, mid_pass_time)

# Check roll
if abs(aircraft_position['roll_angles']) > 15:
    print('Aircraft not level')
    print(aircraft_position['roll_angles'])
    print(aircraft_position['roll_angles'])
elif abs(aircraft_pass_position['roll_angles']) > 10:
    print('Aircraft was not level')
    print(aircraft_pass_position['roll_angles'])
        
D1 = haversine(aircraft_position['lon'], aircraft_position['lat'], pass_lon1, 
                pass_lat1, aircraft_pass_position['alt'])
D2 = haversine(aircraft_position['lon'], aircraft_position['lat'], pass_lon2, 
                pass_lat2, aircraft_pass_position['alt'])
D = (D1 + D2)/2

print('Distance to cloud start: ', D1, 'm')
print('Distance to cloud end: ', D2, 'm')
print('Distance to cloud mid: ', + D)

if distance_override:
    D = D3
    print('Overriding distance to: ', D)
else:
    print('Using Distance to cloud mid: ', D)

if ffc:
    # Set Constants for edge detection:
    # How white vs grey (this might need to be set by trial and error)    
    WHITENESS_THRESHOLD = 200
    # line thickness of box
    THICKNESS = 10
    # The part of every photo is just ground set to 0 if whole photo is cloud
    NOTSKY = 325

    img = io.imread(image_file)
    img_grey = color.rgb2gray(img)
    img_grey = cv2.bilateralFilter(img, 18, 100, 100)
    mask = np.all(img > WHITENESS_THRESHOLD, axis=-1)
    img_grey[~mask] = 0
    cv_grey = cv2.GaussianBlur(img_grey.astype(np.uint8) * 255, (7, 7), 0)
    edges = cv2.Canny(cv_grey, 0, 120)
    edges[NOTSKY::,:]=0
    edges[:,0:20]=0
    edges[:,-15::]=0
    edges[0:20,:]=0

if rfc:
    # Set Constants for edge detection:
    # How white vs grey (this might need to be set by trial and error)    
    WHITENESS_THRESHOLD = 200
    # line thickness of box
    THICKNESS = 10
    # The part of every photo is just ground set to 0 if whole photo is cloud
    NOTSKY = 325

    img = io.imread(image_file)
    img_grey = color.rgb2gray(img)
    img_grey = cv2.bilateralFilter(img, 9, 75, 75)
    mask = np.all(img > WHITENESS_THRESHOLD, axis=-1)
    img_grey[~mask] = 0
    cv_grey = cv2.GaussianBlur(img_grey.astype(np.uint8) * 255, (7, 7), 0)
    edges = cv2.Canny(cv_grey, 50, 250)
    edges[NOTSKY::,:]=0
    edges[:,0:20]=0
    edges[:,-15::]=0
    edges[0:20,:]

# Find contours and sort by area
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)

# Draw the contours on the original image
thickness = 8  # Adjust this value to control the thickness of the drawn contours
edge_image = cv2.imread(image_file).copy()
cv2.drawContours(edge_image, contours, -1, (0, 255, 0), thickness)
cv2.imwrite('cloud_edge.png', edge_image)
cloud_edge=Image.open('cloud_edge.png')


found_points = []
search_range = 380
if x_target_override:
    x_target = x_target
else:
    x_target = 380


def find_intersection(x_target):
    """
    Finds the intersection point with the given x-coordinate in the contours.

    Parameters:
    x_target (int): The x-coordinate to search for in the contours.

    Returns:
    tuple or None: The intersection point (x, y) if found, None otherwise.
    """
    for contour in contours:
        for point in contour:
            x, y = point[0]
            if x == x_target:
                return (x, y)
    return None


# Search for intersection
for offset in range(search_range):
    # Check current x_target
    result = find_intersection(x_target)
    if result:
        found_points.append(result)
        break

    # Check x_target + offset
    result = find_intersection(x_target + offset)
    if result:
        found_points.append(result)
        x_target += offset
        break

    # Check x_target - offset
    result = find_intersection(x_target - offset)
    if result:
        found_points.append(result)
        x_target -= offset
        break


if pixel_height_override:
    pixel_height = 576-yo
    print('Overriding pixel height to: ', yo)
else:
    if found_points:
        x, y = found_points[-1]
        print(f"Contour intersects x={x_target} at y={y}")
    else:
        print(f"No contours intersect within the search range of {search_range} pixels from x={x_target}")
        print('Using dummy value for y y=[432]')
        y=432



    print('Pixel height y coord: ', y)

    try:
        pixel_height = 576- y
    except TypeError:
        pixel_height = 576- y[-1]




pixel_height_adj=pixel_height-576/2
print('Pixel height above center: ', pixel_height_adj)

if ffc:
    calculator1=hc.CloudHeightCalculator(pixel_height_adj,D,aircraft_pass_position['pitch']-3)
    
if rfc:
    calculator1=hc.CloudHeightCalculator(pixel_height_adj,D,-aircraft_pass_position['pitch']+3)
   
height_corrected1 =calculator1.calculate_height()



# correct height of center of frame 
if ffc:
    x1=D*math.tan(math.radians(aircraft_pass_position['pitch']-3))
   
if rfc:
    x1=D*math.tan(math.radians(-aircraft_pass_position['pitch']+3))
    



# cloud top height is height of cloud edge + aircraft height 
# + height adjustment of the center of the frame
if ffc:    
    cloud_top_height1 = height_corrected1 + aircraft_position['alt']+x1
   
if rfc: 
    cloud_top_height1 = height_corrected1 + aircraft_position['alt']+x1
    

print('the estimated cloud top height is: ', cloud_top_height1)
print('the pass height was: ', aircraft_pass_position['alt'])
print('pass number: ', pass_number)


pass_diff1=cloud_top_height1-aircraft_pass_position['alt']

img = io.imread(image_file)
fig, ax = plt.subplots(figsize=(14, 10))
plt.imshow(img)
try:
    plt.plot(x_target, 576-pixel_height, 'ro')
    
    # Add text at the red dot position
    plt.text(150, 576 - pixel_height+30, f'D: {int(D1)}m, CTH: {int(cloud_top_height1)} m, APH: {int(aircraft_pass_position["alt"])} m', color='k', fontsize=12, ha='left', va='bottom')
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
  
plt.title('Pass {}_{}, Timestamp: {}.'.format(pass_number,camera_name, timestamp)+'\n Estimated plane pass height between {}m below cloud top'.format(int(pass_diff1)), fontsize=20)

try:
    plt.savefig('pass_{}_{}_{}.png'.format(pass_number, timestamp,camera_name),
                 bbox_inches='tight', pad_inches=0.5)
    print('saving to: ', 'pass_{}_{}_{}.png'.format(pass_number,timestamp,camera_name))
except: 
    plt.savefig(home+'pass_{}_{}_{}.png'.format(pass_number, timestamp,camera_name),
                 bbox_inches='tight', pad_inches=0.5)
    print('saving to: ', home+'pass_{}_{}_{}.png'.format(pass_number,timestamp,camera_name))


df.at[0,'Distance'] = D
df.at[0,'plane_height'] = aircraft_position['alt']
df.at[0,'pass_height'] = aircraft_pass_position['alt']
df.at[0,'cloud_height'] = cloud_top_height1
df.at[0,'cloud_above_plane_height'] =  pass_diff1
df.at[0,'roll'] = aircraft_position['roll_angles']
df.at[0,'pitch'] = aircraft_pass_position['pitch']    
df.at[0,'pixel_height'] = pixel_height
df.at[0,'x_target'] = x_target
df.at[0,'pass_number'] = pass_number
df.at[0,'camera'] = camera
df.at[0,'timestamp'] = timestamp

try:
    df.to_csv('cloud_heights_'+date+timeframe+'.csv')
    print('saving to: ', 'cloud_heights_'+date+timeframe+'.csv')
except:
    df.to_csv(home+'cloud_heights_'+date+timeframe+'.csv')
    print('saving to: ', home+'cloud_heights_'+date+timeframe+'.csv')

plt.show()
plt.cla()