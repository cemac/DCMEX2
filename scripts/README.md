
1. processvids.py 
   * Takes camera and date args.
   * script contains paths to lag table, output folder and faam-videos
   * filters faam video to create clean images
   * outputs _clean version
   * mainly applicable to ffc video which has large distortion 
2. output_frames.py
   * takes camera and data
   * contains root output, input folders and lag table
3. create_frames.py
   * takes camera and date
   * creates pass_frames/date/camera/
   * sorts by pass, then labels frames with blue sky,
   * creates thumbnail with usable frames highlighted in green
4. cloudtop_above_pass_all.py
   * takes --date_to_use 20220731 --ffc
   * creates cloud_heights/date/camera
   * will calculate heights if bluesky is detected , will leave if not.
   * creates a csv of time, pass  and cloud height delected etc