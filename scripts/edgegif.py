import cv2
import glob
import os

imtyp='mask'
camera='ffc'
date='20220730'

if imtyp=='mask':
    folder_name='mask_im'
    fname='cloud_mask'
    outname='mask'
else:
    folder_name='edge_im'
    outname='edges'
    fname='cloud_edge'


# Grab images in order
image_files = sorted(
    glob.glob("{}/{}/{}/{}*.png".format(folder_name,date,camera,fname)),
    key=lambda x: int(os.path.basename(x).split(fname)[-1].split(".png")[0])
)
num_frames = len(image_files)
print(f"Found {num_frames} frames.")

# Target duration 60–90s
target_duration = 75  # seconds
fps = num_frames / target_duration
print(f"Using fps = {fps:.2f}")

# Get frame size from the first image
frame = cv2.imread(image_files[0])
height, width, _ = frame.shape
frame_size = (width, height)

# Create VideoWriter for MP4
# 'mp4v' is a common codec; you can also try 'H264' if supported
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('{}_{}.mp4'.format(fname,date), fourcc, fps, frame_size)

# write all frames
for fname in image_files:
    img = cv2.imread(fname)
    out.write(img)  # OpenCV expects BGR, which cv2.imread gives by default

out.release()
print("MP4 created successfully!")
