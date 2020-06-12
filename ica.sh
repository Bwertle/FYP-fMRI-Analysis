#!/bin/bash

module load fsl

basePath=$1

while IFS=' ' read -rp 'List groups to run ICA analysis: ' groups; do
for group in $groups 
#for group in patients_1 patients_2 # note: make group names inputs to file
do 
    path="$basePath/$group"
    echo "Running melodic: $path"
   
    # get list of files which have been pre-processed
    list_bold=`find $path -name *preproc_bold.nii.gz`
    echo "List of bold files $list_bold"
    
    # denoise data
    for bold in $list_bold
    do
        mask=${bold:0:(-19)}
        mask+="brain_mask.nii.gz"
        outfile=${bold:0:-61}
        outfile+="_stripped_preproc.nii.gz"
        echo "$mask $outfile"
        
        # skull strip
        fslmaths $bold -mas $mask $outfile # strip brain to remove skull
        
        # denoise
        python denoise.py $outfile $bold # run python denoise script 

    done
    
    # write txt files to list nifti files for each group
#    find $path -name *stripped_preproc.nii.gz | sort -n > "$path/list.txt"
    find $path -name *denoised.nii.gz | sort -n > "$path/list.txt"
	
    # run melodic
    echo "Running melodic on $group"
    melodic -i "$path/list.txt" -o "$path/melodic" --Oall --report -d 15 

done

done 
