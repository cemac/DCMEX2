import cv2
import numpy as np
import imageio
from skimage import color, io
from datetime import datetime, timedelta
# -----------------------------
# Parameters
# -----------------------------

input_file = "faam-video-ffc_faam_20220731_r0_c308_173245_1hz.mp4"
mp4_out = "faam-video-ffc_faam_20220731_clean_c308_173245_1hz.mp4"

start_time_sec = 0   # 00:00:00
end_time_sec   = 59*60   # 00:59:00

# Speed-up factors
mp4_speedup = 1

# Video start timestamp start time is 10 after time stamp
video_start_str = "17:32:45"
video_start = datetime.strptime(video_start_str, "%H:%M:%S")

# -----------------------------
# Open input video
# -----------------------------
cap = cv2.VideoCapture(input_file)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Frame range
start_frame = int(start_time_sec * fps)
end_frame   = int(end_time_sec * fps)

cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

# -----------------------------
# Prepare MP4 writer
# -----------------------------
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_mp4 = cv2.VideoWriter(mp4_out, fourcc, fps*mp4_speedup, (width, height))

frame_idx = start_frame
while frame_idx < end_frame:
    ret, frame = cap.read()
    if not ret:
        break
    
    cleaned_frame = np.zeros_like(frame)
    for c in range(3):
        channel = frame[:, :, c]
        channel = cv2.bilateralFilter(channel, 12, 100, 100)
        #channel = cv2.GaussianBlur(channel, (7, 7), 0)
        # cleaned_frame: already filtered in all 3 channels
        cleaned_frame[:, :, c] = channel
        
    # cleaned_frame: already filtered in all 3 channels
    cleaned_frame = cv2.addWeighted(cleaned_frame, 1.5, cleaned_frame, -0.5, 0)
    # -----------------------------
    # Add timestamp
    # -----------------------------
    elapsed_seconds = (frame_idx - start_frame) / fps
    current_time = video_start + timedelta(seconds=elapsed_seconds)
    timestamp_str = current_time.strftime("%H:%M:%S")

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)  # white
    thickness = 2

    (text_width, text_height), baseline = cv2.getTextSize(timestamp_str, font, font_scale, thickness)
    x = frame.shape[1] - text_width - 10
    y = frame.shape[0] - 10

    cv2.putText(cleaned_frame, timestamp_str, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

    
    # -----------------------------
    # Write MP4 frames
    # -----------------------------
    
    out_mp4.write(cleaned_frame)

    frame_idx += 1

# -----------------------------
# Release video writer
# -----------------------------
cap.release()
out_mp4.release()

print("Done! MP4 created.")
