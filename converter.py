from nipype.interfaces.dcm2nii import Dcm2niix
import os
import argparse
import glob

def convert(path):
    '''
        Converts .dcms to .nii.gz

        Input:
            path: (path) Path to folder containing DICOMS
    '''
    dirs = path.split('/')

    if dirs[-1] == 'anat':
        filename = dirs[-2]+'_T1w'
        print(filename)
    elif dirs[-1] =='func':
        filename = dirs[-2]+'_task-rest_bold'
        print(filename)

    converter = Dcm2niix()
    converter.inputs.source_dir = path
    converter.inputs.output_dir = path
    converter.inputs.out_filename = filename
    converter.run()

    print("Completed conversion: {}".format(path))
    return

def remove_dcms(path):
    '''
        Recursively remove all dicoms in path.

        Input:
            - path: (path) Path to remove all dicoms from
    '''
    dcm_list = glob.glob(os.path.join(path,"**/*dcm"), recursive=True)
    print("Removing {} dicoms".format(len(dcm_list)))
    for dcm in dcm_list: 
        os.remove(dcm)
    return

def convert_data(path):
    '''
        Runs data conversion from .dcm to .nii.gz. 

        Input: 
            - path: (path) Path containing all .dcm files
    '''
    folder_list = glob.glob(os.path.join(path,'**/*dcm'), recursive=True)
    #print(len(folder_list))
    for i in range(len(folder_list)):
        folder = folder_list[i]    
        folder = '/'.join(folder.split('/')[:-1])
        #print(folder)
        folder_list[i] = folder

    folder_list = list(set(folder_list))
    print("Number of folders: {}".format(len(folder_list)))

    for folder_path in folder_list: 
        print(folder_path)
        path = folder_path
        convert(path)
        remove_dcms(path)
    return

def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '-I', '--input', required=True, help='Path to patient folders')

    args = vars(ap.parse_args())

    input_path = args['input']

    control_path = os.path.join(input_path, 'controls')
    patient_path = os.path.join(input_path, 'patients')

    convert_data(control_path)
    convert_data(patient_path)

if __name__ == "__main__":
    main()
