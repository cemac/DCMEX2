#!/bin/bash
echo "activating python env"
conda activate DCMEX


dates=(20220727 20220730 20220801 20220807)


# Loop over each date
for date in "${dates[@]}"; do
    echo "Running FFC for date $date"
    python cloudtop_above_pass_all.py --date_to_use "$date" --ffc

    echo "Running RFC for date $date"
    python cloudtop_above_pass_all.py --date_to_use "$date" --rfc
    echo "COMPLETE DAY $date"
done


echo "complete"
