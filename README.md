# Final-Year-Project #
This is the work of Rebekah Chiu for the project functional MRI for Motor Neuron Disease. This pipeline is for usage on the [Monash M3 MASSIVE Cluster](https://docs.massive.org.au/index.html) with the [Monash XNAT](https://mbi-xnat.erc.monash.edu.au/app/template/Login.vm#!) server. Before running any scripts, a Python virtual environment should be created and all packages in **requirements.txt** installed.

Order of usage
------------

### data.sh

Downloads data from Monash XNAT server and converts DICOMs to NIFTI format. It also reorganises data into the BIDS format. Allows choice of subject numbers and whether to download patients only, controls only or both presuming that controls are labelled \_C0* and pateients are labeled \_0*. Runs on a single CPU core, suggested 8GB RAM. 

```
data.sh input_path
```


### [fMRIPrep](https://fmriprep.readthedocs.io/en/stable/) 
fMRIPrep can now be run to pre-process the downloaded data. Use the command below to run fMRIPrep. It's suggested to breakdown each fMRIPrep run into a few participants using the `--participant label` flag. Suggested 48 threads with 8GB RAM per CPU. 
```
fmriprep input_folder output_folder participant --nthreads number_of_threads --mem-mb memory_allocation -w working_directory
```


### ica.sh

Runs denoising of the data using a Python script and group ICA with FSL MELODIC. Runs on a single CPU, suggested 16GB RAM.

```
data.sh Base_path_for_all_groups
```


### t-test.sh
Bash script to run dual regression for each group and appropriate t-Test. 

Independent t-Test (default) 
```
t-test.sh -x group1Path -y group2Path -c group1_components -d group2_components
```
Paired t-Test
```
t-test.sh -x group1Path -y group2Path -c group1_components -d group2_components -p
```
