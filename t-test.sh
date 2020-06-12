#!/bin/bash

unset group1Path group2Path group1_comp group2_comp

test_type="True"

while getopts 'x:y:c:d:' flag
do
	case $flag in
	 x) group1Path="$OPTARG" ;;
	 y) group2Path="$OPTARG" ;;
	 c) group1_comp="$OPTARG" ;;
	 d) group2_comp="$OPTARG" ;; 
     p) test_type="False" ;;
     *) echo "Usage: t-test.sh -x group1Path -y group2Path -c group1_comp -d group2_comp"
	esac
done

echo "Paths: $group1Path $group2Path"


group1IC="$group1Path/melodic/melodic_IC.nii.gz"
group2IC="$group2Path/melodic/melodic_IC.nii.gz"

# Output list of denoised time series files for each group as txt
for group in $group1Path $group2Path; do
	find $group -type f -name "*denoised.nii.gz" | sort -n > "$group/list.txt"
done

# Perform dual regression using FSL
dual_regression $group1IC 0 -1 500 "$group1Path/indivMELODIC" `cat "$group1Path/list.txt"`
dual_regression $group2IC 0 -1 500 "$group2Path/indivMELODIC" `cat "$group2Path/list.txt"`

# Output list of components of interest for each group as txt
for group in $group1Path $group2Path; do
	find $group -type f -name "*stage2_subject000??.nii.gz" | sort -n > "$group/indivList.txt"
done

# Run t-test.py
python t-test.py --group1 "$group1Path/indivList.txt" --group2 "group2Path/indivList.txt" --group1_comp $group1_comp --group2_comp $group2_comp --independent $test_type
