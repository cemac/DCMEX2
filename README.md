# Stand Alone Tool

## Annotated pass pictures

Can be found on JASMIN here:

`/gws/nopw/j04/dcmex/users/hburns/DCMEX2/cloud_heights/images`

## Python environment for stand-alone tool

`/gws/nopw/j04/dcmex/users/hburns/DCMEX2/DCMEX2.yml`

to install this please use 

`conda env create -f DCMEX2.yml`

## Using the tool

1. Activate the python environment `conda activate cloud_heights`
2. run the python script e.g.
   `python /gws/nopw/j04/dcmex/users/hburns/DCMEX2/cloud_height_standalone.py --file /gws/nopw/j04/dcmex/users/hburns/DCMEX2/images/20220730/pass_276_ffc/frame_c307_20220730_165926_sky_bluesky_ffc.png --px 575 --py 300 --D 6000`

 * this uses absolute paths but will work with relative paths as well or 
   * `export DCMEX2pth=/gws/nopw/j04/dcmex/users/hburns/DCMEX2/`
   * `export cldimgpth=/gws/nopw/j04/dcmex/users/hburns/DCMEX2/cloud_heights/images`
   * and run
     `python $DCMEX2pth/cloud_height_standalone.py --file cldimgpth/20220730/pass_276_ffc/frame_c307_20220730_165926_sky_bluesky_ffc.png --px 380 --py 300 --D 5000`

### tool arguments:

* `-h` help prints the help string similar to this
* `--file` (required) relative or absolute path to file
* `--px` (optional) pixel x co-ordinate override. *Default mid point originating autosearch for cloud edge* 
* `--py` (optional) pixel y co-ordinate override. *Default - autodetected cloud edge*
* `--D` (optional) Distance override. *Default - mid point of pass*

## Outputs

* prints to screen variables used and heights calculated
* prints to csv in current working directory all variables used in calculations including aircraft data
* saves a png of new annotated figure (you must rename to prevent overwriting with different pixel point) 
