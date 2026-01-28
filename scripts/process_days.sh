#!/bin/bash

echo "activating python env"
conda activate cloud_heights
python processvids.py --date_to_use 20220731 --ffc
python output_frames.py --date_to_use 20220731 --ffc
python create_fames_df.py --date_to_use 20220731 --ffc
python find_the_usable_photos.py --date_to_use 20220731 --ffc
python cloudtop_above_pass_all.py --date_to_use 20220731 --ffc

python processvids.py --date_to_use 20220731 --rfc
python output_frames.py --date_to_use 20220731 --rfc
python create_fames_df.py --date_to_use 20220731 --rfc
python find_the_usable_photos.py --date_to_use 20220731 --rfc
python cloudtop_above_pass_all.py --date_to_use 20220731 --rfc
