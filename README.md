<div align="center">
<a href="https://www.cemac.leeds.ac.uk/">
  <img src="https://github.com/cemac/cemac_generic/blob/master/Images/cemac.png"></a>
  <br>
</div>

# DCMEX 2 #


[![DOI](https://zenodo.org/badge/558317218.svg)](https://zenodo.org/doi/10.5281/zenodo.13532812)

[![GitHub release](https://img.shields.io/github/release/cemac/DCMEX2.svg)](https://github.com/cemac/DCMEX2/releases) [![GitHub top language](https://img.shields.io/github/languages/top/cemac/DCMEX2.svg)](https://github.com/cemac/DCMEX2) [![GitHub issues](https://img.shields.io/github/issues/cemac/DCMEX2.svg)](https://github.com/cemac/DCMEX2/issues) [![GitHub last commit](https://img.shields.io/github/last-commit/cemac/DCMEX2.svg)](https://github.com/cemac/DCMEX2/commits/master) [![GitHub All Releases](https://img.shields.io/github/downloads/cemac/DCMEX2/total.svg)](https://github.com/cemac/DCMEX2/releases) ![GitHub](https://img.shields.io/github/license/cemac/DCMEX2.svg) 


# DCMEX2 - Automated Measuring of cloud height from aircraft videos

This repository is part of the [Deep Convective Microphysics Experiment (DCMEX)](https://cloudsense.ac.uk/dcmex/) project. This repository follows on from the work done in [DCMEX repository](https://github.com/cemac/DCMEX) which automated measuring cloud heights from ground camera timelapses. 


The code here attempts to automatically detect the top height from [FAAM]() aircraft video during a 2022 field campaign using:

* Aircraft instrumentation data, such as GPS, altitude etc
* Video footage from air craft mounted cameras.


The footage was preproccessed to remove noise and separated out into frames, information on timings of the cloud top passes were used to catelogue frames into the relevant cloud pass groups. We then selected images that contained sky and used open CV image processing tools to detected the cloud top in in the image. This information alongside estimated distance from the aircraft instrument data and cloud pass dataset can be used in optical equations to estimate the cloud top height. 

All the methodology is outlined in the [DCMEX wiki](https://github.com/cemac/DCMEX2/wiki)

# DCMEX2 - StandAlone Tools.

We also provide standalone tools:

1. `height_calculator.py` 
2. `cloud_height_only_standalone.py` Estimate cloud top height form any frame including not from cloud top passes. Must give manual distance estimate and pixel location.
3. `cloud_height_pass_standalone.py` Estimate cloud top height from pass images, option to override pixel and distance for height estimation. 
3. `procesvids_single.py` process famm video to remove noise and clip and speed up as desired to output mp4s and GIFs.

more information on these tools can be found on the [stand alone tools wiki](https://github.com/cemac/DCMEX2/wiki/Stand-Alone-Tools)


# Requirements

python requirements are provided in the DCMEX2.yml file


# Documentation

Detailed documentation of the the tools and methodology and dataset used is provided in [this repositories wiki](ttps://github.com/cemac/DCMEX2/wiki).

# Acknowledgements #

Tool developers: Helen Burns, Declan Finney, Alan Blyth. Data Archiving: Josh Hampton. Data collection:  Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A.

# Licence information #

This code is Licensed under the GPL-3 license

# References

 * Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A. (2023): DCMEX: cloud images from the NCAS Camera 11 from the New Mexico field campaign 2022. NERC EDS Centre for Environmental Data Analysis, 15 December 2023. [doi:10.5285/b839ae53abf94e23b0f61560349ccda1](https://dx.doi.org/10.5285/b839ae53abf94e23b0f61560349ccda1)
*  Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A. (2023): DCMEX: cloud images from the NCAS Camera 12 from the New Mexico field campaign 2022. NERC EDS Centre for Environmental Data Analysis, 15 December 2023. [doi:10.5285/d1c61edc4f554ee09ad370f6b52f82ce](https://dx.doi.org/10.5285/d1c61edc4f554ee09ad370f6b52f82ce)
* Declan Finney, James Groves, Dan Walker, David Dufton, Robert Moore, David Bennecke, Vicki Kelsey, R. Stetson Reger, Kasia Nowakowska, James Bassford, & Alan Blyth. (2023, April 25). Timelapse footage of deep convective clouds in New Mexico produced during the DCMEX field campaign (Version 1). Zenodo. [https://doi.org/10.5281/zenodo.7756710](Declan Finney, James Groves, Dan Walker, David Dufton, Robert Moore, David Bennecke, Vicki Kelsey, R. Stetson Reger, Kasia Nowakowska, James Bassford, & Alan Blyth. (2023, April 25). Timelapse footage of deep convective clouds in New Mexico produced during the DCMEX field campaign (Version 1). Zenodo. https://doi.org/10.5281/zenodo.7756710)
* Finney, D. L. and Blyth, A. M. and Gallagher, M. and Wu, H. and Nott, G. J. and Biggerstaff, M. I. and Sonnenfeld, R. G. and Daily, M. and Walker, D. and Dufton, D. and Bower, K. and B\"oing, S. and Choularton, T. and Crosier, J. and Groves, J. and Field, P. R. and Coe, H. and Murray, B. J. and Lloyd, G. and Marsden, N. A. and Flynn, M. and Hu, K. and Thamban, N. M. and Williams, P. I. and Connolly, P. J. and McQuaid, J. B. and Robinson, J. and Cui, Z. and Burton, R. R. and Carrie, G. and Moore, R. and Abel, S. J. and Tiddeman, D. and Aulich, G (2024):Deep Convective Microphysics Experiment (DCMEX) coordinated aircraft and ground observations: microphysics, aerosol, and dynamics during cumulonimbus development. ESSD-16-2141-2163 [https://essd.copernicus.org/articles/16/2141/2024/](https://essd.copernicus.org/articles/16/2141/2024/)