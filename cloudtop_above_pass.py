
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
import height_calculator as hc
import glob
import os

#framelist='frame_c301_20220723_172455_sky_bluesky.png'
file_name_list = glob.glob('20220723/pass_97_b_*_ffc/*')
dataset = xr.open_dataset('core_faam_20220723_v005_r0_c301_1hz.nc')
cloud_passes = pd.read_csv('FAAM_cloudpass_info.csv')
ffc=True
rfc=False

def extract_pass_number(file_name):
    filepath_parts = file_name.split('/')
    pass_number= filepath_parts[1].split('_')[1]
    return pass_number

def extract_timestamp_from_filename(filepath):
    filepath_parts = filepath.split('/')
    filename_parts = filepath_parts[2].split('_')
    camera= filepath_parts[1].split('_')[3]
    date = filename_parts[2]
    times = filename_parts[3]
    full_timestamp = pd.to_datetime(date+'_'+times, format="%Y%m%d_%H%M%S")
    return [camera, full_timestamp] 

# Define a function to find the closest roll_time and get the corresponding roll_angle
def get_closest_roll_angle(aircraft_df, frame_time):
    # Calculate the absolute difference between frame_time and all roll_times
    diffs = abs(aircraft_df['times'] - frame_time)
    # Find the index of the minimum difference
    min_diff_index = diffs.idxmin()
    # Return the corresponding roll_angle
    return aircraft_df.loc[min_diff_index]

def extract_variables(dataset):
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
    aircraft_df = pd.DataFrame({'times': roll_times_pd, 'lat': lat, 'lon' : lon, 'pitch' : pitch, 'alt': alt, 'roll_angles': roll_angle, 'veln': veln, 'vele': vele})
    return aircraft_df

def extract_cloud_pass_info(cloud_passes, pass_number):
    pass_info = cloud_passes.loc[int(pass_number)-1]
    cloud_lat1 = pass_info['start_lat']
    cloud_lon1 = pass_info['start_lon']
    cloud_lat2 = pass_info['end_lat']
    cloud_lon2 = pass_info['end_lon']
    start_time = datetime.strptime(pass_info['start_datetime'], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(pass_info['end_datetime'], '%Y-%m-%d %H:%M:%S')
    return [cloud_lat1, cloud_lon1, cloud_lat2, cloud_lon2, start_time, end_time]

def haversine( lon1, lat1, lon2, lat2, alt):
    R = 6371e3 + alt # radius of Earth in metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = phi2-phi1
    
    lambda1 = math.radians(lon1)
    lambda2 = math.radians(lon2)
    dlambda = lambda2-lambda1

    a = math.sin(dphi/2) * math.sin(dphi/2) + math.cos(phi1) * math.cos(phi1) * math.sin(dlambda/2) * math.sin(dlambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c
    
    return d

for file_name in file_name_list:
    # Get the distance
    #extract info
    camera, timestamp = extract_timestamp_from_filename(file_name)
    pass_number = extract_pass_number(file_name)
    aircraft_df = extract_variables(dataset)
    aircraft_position = get_closest_roll_angle(aircraft_df, timestamp)
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
            
    D1 = haversine(aircraft_position['lon'], aircraft_position['lat'], pass_lon1, pass_lat1, aircraft_pass_position['alt'])
    D2 = haversine(aircraft_position['lon'], aircraft_position['lat'], pass_lon2, pass_lat2, aircraft_pass_position['alt'])
    D = (D1 + D2)/2

    print('Distance to cloud start: ', D1, 'm')
    print('Distance to cloud end: ', D2, 'm')
    print('Distance to cloud mid: ', D, 'm')

    print('Using Distance to cloud mid: ', + D)
    distance_override=False
    pass_portion = 0.8
    if distance_override:
        D = (D1 + D2) * pass_portion
        print('Overriding distance to: ', D)

    # Set Constants for edge detection:
    # How white vs grey (this might need to be set by trial and error)    
    WHITENESS_THRESHOLD = 150
    # line thickness of box
    THICKNESS = 10
    # The part of every photo is just ground set to 0 if whole photo is cloud
    NOTSKY = 325

    img = io.imread(file_name)
    img_grey = color.rgb2gray(img)
    img_grey = cv2.bilateralFilter(img, 18, 100, 100)
    mask = np.all(img > WHITENESS_THRESHOLD, axis=-1)
    img_grey[~mask] = 0
    cv_grey = cv2.GaussianBlur(img_grey.astype(np.uint8) * 255, (7, 7), 0)
    edges = cv2.Canny(cv_grey, 0, 200)
    edges[NOTSKY::,:]=0
    edges[:,0:20]=0
    edges[:,-15::]=0

    # Find contours and sort by area
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                    cv2.CHAIN_APPROX_SIMPLE)

    # Draw the contours on the original image
    thickness = 8  # Adjust this value to control the thickness of the drawn contours
    edge_image = cv2.imread(file_name).copy()
    cv2.drawContours(edge_image, contours, -1, (0, 255, 0), thickness)
    cv2.imwrite('cloud_edge.png', edge_image)
    cloud_edge=Image.open('cloud_edge.png')

    x_target = 380
    found_points = []

    for contour in contours:
        for point in contour:
            # point is a 3D array: [[x, y]]
            x, y = point[0]
            if x == x_target:
                found_points.append((x, y))

    if found_points:
        # If there are multiple points, you can decide how to handle them
        # Here, we'll just pick the first one for simplicity
        x, y = found_points[0]
        print(f"Contour intersects x={x_target} at y={y}")
    else:
        print(f"No contours intersect x={x_target} trying to x={x_target+1}")
        x_target = 351
        found_points = []

        for contour in contours:
            for point in contour:
                # point is a 3D array: [[x, y]]
                x, y = point[0]
                if x == x_target:
                    found_points.append((x, y))

        if found_points:
            # If there are multiple points, you can decide how to handle them
            # Here, we'll just pick the first one for simplicity
            x, y = found_points[0]
            print(f"Contour intersects x={x_target} at y={y}")
        else:
            print(f"No contours intersect x={x_target+1}")

    pixel_height = 576- y   
    pixel_height_override = False
    yo = 130
    if pixel_height_override:
        pixel_height = 576-yo
        print('Overriding pixel height to: ', pixel_height)

    pixel_height-576/2
    calculator=hc.CloudHeightCalculator(-33,D,aircraft_pass_position['pitch']-3)
    height_corrected =calculator.calculate_height()
    print(height_corrected)
    x=D*math.tan(math.radians(aircraft_pass_position['pitch']-3))
    cloud_top_height = height_corrected + aircraft_position['alt']+x
    print('the estimated cloud top height is: ', cloud_top_height)
    print('the pass height was: ', aircraft_pass_position['alt'])
    pass_diff=cloud_top_height-aircraft_pass_position['alt']
    img = io.imread(file_name)
    
    plt.plot(x_target, 576-pixel_height, 'ro')

    # Add text at the red dot position
    plt.text(x_target+10, 576 - pixel_height, f'Height: {int(cloud_top_height)} m', color='k', fontsize=12, ha='left', va='bottom')
    plt.text(x_target-120, 480, f'aircraft pass height: {int(aircraft_pass_position['alt'])} m', color='k', fontsize=12, ha='left', va='bottom')
    #plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    # Display the roll_angle
    plt.text(0.1, 0.5, f'{aircraft_position['roll_angles']:,.2f}',
                color='red',
                horizontalalignment='left',
                verticalalignment='center',
                transform = plt.gca().transAxes,alpha=0.4)
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
    plt.title('Pass {}, Timestamp: {}.'.format(pass_number, timestamp)+'\n Estimated plane flew {}m below cloud top'.format(int(pass_diff)), fontsize=20)
    os.makedirs('figures/pass_{}/'.format(pass_number), exist_ok=True)
    plt.savefig('{}.png'.format(file_name.split('/')[-1].split('.')[0]))