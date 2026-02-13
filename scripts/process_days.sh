#!/bin/bash                                                                                                                                                                                                       
#SBATCH --job-name=new1                                                                                                                                                                                      
#SBATCH --partition=standard
#SBATCH --qos=high                                                                                                                                                                                                
#SBATCH --time=18:00:00                                                                                                                                                                                           
#SBATCH --cpus-per-task=3                                                                                                                                                                                         
#SBATCH --mem=16G                                                                                                                                                                                                 
#SBATCH --account=dcmex                                                                                                                                                                                           
#SBATCH --output=logs/%x_%A_%a.out                                                                                                                                                                                
#SBATCH --error=logs/%x_%A_%a.err


echo "activating python env"
conda activate cloud_heights


dates=(20220725)


# Loop over each date
for date in "${dates[@]}"; do
    python processvids.py --date_to_use $date --ffc
    python output_frames.py --date_to_use $date --ffc
    python create_fames_df.py --date_to_use $date --ffc
    python find_the_usable_photos.py --date_to_use $date --ffc
    python cloudtop_above_pass_all.py --date_to_use $date --ffc

    python processvids.py --date_to_use $date --rfc
    python output_frames.py --date_to_use $date --rfc
    python create_fames_df.py --date_to_use $date --rfc
    python find_the_usable_photos.py --date_to_use $date --rfc
    python cloudtop_above_pass_all.py --date_to_use $date --rfc
done
