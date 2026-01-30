#!/bin/bash                                                                                                                                                                                                       
#SBATCH --job-name=dcmex0807                                                                                                                                                                                      
#SBATCH --partition=standard
#SBATCH --qos=high                                                                                                                                                                                                
#SBATCH --time=12:00:00                                                                                                                                                                                           
#SBATCH --cpus-per-task=3                                                                                                                                                                                         
#SBATCH --mem=16G                                                                                                                                                                                                 
#SBATCH --account=dcmex                                                                                                                                                                                           
#SBATCH --output=logs/%x_%A_%a.out                                                                                                                                                                                
#SBATCH --error=logs/%x_%A_%a.err


echo "activating python env"
conda activate DCMEX


dates=(20220731)


# Loop over each date
for date in "${dates[@]}"; do
    echo "Running FFC for date $date"
    python cloudtop_above_pass_all.py --date_to_use "$date" --ffc

    echo "Running RFC for date $date"
    python cloudtop_above_pass_all.py --date_to_use "$date" --rfc
    echo "COMPLETE DAY $date"
done


echo "complete"
