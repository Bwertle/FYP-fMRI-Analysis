# Final-Year-Project #
This is the work of Rebekah Chiu for the project functional MRI for Motor Neuron Disease. This pipeline is for usage on the [Monash M3 MASSIVE Cluster](https://docs.massive.org.au/index.html) with the [Monash XNAT](https://mbi-xnat.erc.monash.edu.au/app/template/Login.vm#!) server. Before running any scripts, a Python virtual environment should be created and all packages in **requirements.txt** installed.

Order of usage
------------

### data.sh
Downloads data from Monash XNAT server and converts DICOMs to NIFTI format. It also reorganises data into the BIDS format. Allows choice of subject numbers and whether to download patients only, controls only or both presuming that controls are labelled \_C0* and pateients are labeled \_0*. Runs on a single CPU core, suggested 8GB RAM. 

Runs python scripts in the following order: 
* download-data.py
* converter.py

```
Usage: `data.sh input_path`
```


### [fMRIPrep](https://fmriprep.readthedocs.io/en/stable/) 
fMRIPrep can now be run to pre-process the downloaded data. Use the command below to run fMRIPrep. It's suggested to breakdown each fMRIPrep run into a few participants using the `--participant label` flag. Suggested 48 threads with 8GB RAM per CPU. 
```
fmriprep input_folder output_folder participant --nthreads number_of_threads --mem-mb memory_allocation -w working_directory
```


### ica.sh
Runs denoising of the data and group ICA. Runs on a single CPU, suggested 16GB RAM.

The script runs in the following order:
1. Uses fslmaths to brain strip the data using the brain mask
2. Runs denoise.py to remove components identified by fmriprep
3. Runs FSL MELODIC on a single core for each group. 

```
Usage: `data.sh Base_path_for_all_groups `
```


### t-test.sh
Bash script to run dual regression for each group and appropriate t-Test. 

- `t-test.py` can be run as a standalone script to run a t-Test over two groups of data. It requires a .txt file with a list of the dual regression outputs for each group and the components representing key networks. Defaults to run independent t-Test however the paired t-Test can be run with the flag `--independent False`.

```
Usage:
Independent t-Test (default) 
t-test.sh -x group1Path -y group2Path -c group1_components -d group2_components

Paired t-Test
t-test.sh -x group1Path -y group2Path -c group1_components -d group2_components -p
```
