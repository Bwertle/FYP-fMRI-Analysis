import nibabel as nib
import nilearn.image as nii
import pandas as pd
from argparse import ArgumentParser
import os
import json

# parse commandline arguments
parser = ArgumentParser()
parser.add_argument('input')
parser.add_argument('bold_path')

args = parser.parse_args()
input_img = nib.load(args.input)

subject = args.bold_path.split('/')[-1]
path = args.bold_path.split('/')[:-1]

path = '/'.join(path)

# get lists of confound and json files
confounds = [x for x in os.listdir(path) if '.tsv' in x]
json_file = [x for x in os.listdir(path) if 'preproc_bold.json' in x]

# get repetition time
with open(os.path.join(path, json_file[0]), 'r') as f:
    json_data = json.load(f)
#print(json_data)
tr = json_data['RepetitionTime']

#print(tr)

# read confounds
confound_data = pd.read_csv(os.path.join(path,confounds[0]), sep="\t")

# select confounds
confound_columns = ['a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'a_comp_cor_04', 'a_comp_cor_05', 'cosine00', 'cosine01', 'cosine02', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] 

# regress confounds from input image
filt_confound_data = confound_data[confound_columns]
confound_matrix = filt_confound_data.to_numpy()
regressed_img = nii.clean_img(input_img, t_r=tr, confounds=confound_matrix)

# write denoised imaged
outpath = os.path.join(path, subject)
nib.save(regressed_img, os.path.join(path,'denoised.nii.gz'))
