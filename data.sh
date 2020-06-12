#!/bin/bash

INPUT_PATH=$1

module load xnatpy

IFS= read -rp 'Project ID: ' project
IFS= read -rp 'User: ' user
IFS= read -rsp 'Password: ' password

python download-data.py -i $INPUT_PATH --user $user --password $password --project_ID $project

module purge 
module load dcm2niix

python converter.py -i $INPUT_PATH
