import xnat
import os
import glob
import shutil
import argparse
import zipfile
import re

def _get_subject_list(project, patient_list, control_list):
    '''
        Gets list of subjects. 

        Inputs:
            - project: (xnat session project)
            - patient_list: (list) List of patients
            - control_list: (list) List of controls
    '''

    subs = project.subjects
    #print(subs)
    #print(control_list, patient_list)
    if 'all' not in control_list:
        controls = [subject for subject in subs.values() if ("C" in str(subject) and any(sub in str(subject) for sub in control_list))]
    else: 
        controls = [subject for subject in subs.values() if ("C" in str(subject))]

    if 'all' not in patient_list:
        patients = [subject for subject in subs.values() if ("C" not in str(subject) and "DTI" not in str(subject) and any(sub in str(subject) for sub in patient_list))]
    else:
        patients = [subject for subject in subs.values() if ("C" not in str(subject) and "DTI" not in str(subject))]
    
    print(controls, patients)
    return controls, patients

def _make_folders(path):
    '''
        Makes timepoint folders.
    '''
    for i in [0,1,2]:
        os.makedirs(os.path.join(path, 'timepoint_{}'.format(i)), exist_ok=True)
    return

def _make_subject_folders(path):
    '''
        Makes folders for each subject. 

        Input:
            path: (path)
    '''
    folders = ['anat', 'func']
    for _type in folders:
        os.makedirs(os.path.join(path, _type), exist_ok=True)	
        print("Folders created: {}".format(path))
    return

def _move_files(input_path):
    '''
        Moves DICOM files up to allow removal of unnessary tree structure.

        Inputs:
            - input_path: (path) input path to move files in
    '''
    times = os.listdir(input_path)
    #print(subject_list)
    for time in times:
        subject_list = os.listdir(os.path.join(input_path, time))
        #print(times)
        for subject in subject_list:
            path = os.path.join(input_path, time, subject)
            print(path)
            anat_files = glob.glob(os.path.join(path, 'anat', "**/*.dcm"), recursive=True)
            func_files = glob.glob(os.path.join(path, 'func', "**/*.dcm"), recursive=True)
            print(len(anat_files), len(func_files))
            for file in anat_files:
                file_name = file.split('/')[-1]
                os.rename(file, os.path.join(path, 'anat', file_name))
            for file in func_files:
                file_name = file.split('/')[-1]
                os.rename(file, os.path.join(path,  'func', file_name))
            snapshot_files = glob.glob(os.path.join(path, "**/*.gif"), recursive=True)
            for snapshot in snapshot_files:
                os.remove(snapshot)
            _remove_folders(os.path.join(path, 'anat'))
            _remove_folders(os.path.join(path, 'func'))  
    return

def _remove_folders(path):
    '''
        Removes excess tree structures.

        Input:
            - path: (path) Root path to recursively remove folders from.
    '''
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    return 

def download_data(subject_list, path):
    '''
        Downloads data from Monash XNAT and extracts all data from the downloaded zip files. 

        Inputs: 
            - subject_list: (list) All subjects in the group to be downloaded from Monash XNAT. 
            - path: (path) Path to save all downloaded subjects in this group.
    '''


    _make_folders(path)
    counter=0
    for sub_count, subject in enumerate(subject_list):
        counter+=1
        experiments = subject.experiments
        sessions = [x for x in experiments]
        sessions.sort()
        print(subject)
        for sess_count, session in enumerate(sessions):
            if 'PROC' not in experiments[session].label:
                save_path = os.path.join(path, 'timepoint_{}'.format(sess_count), 'sub-{0:02d}'.format(counter))
                #save_path = os.path.join(path, 'timepoint_{}'.format(sess_count), 'sub-{0:02d}'.format(sub_count+1))
                _make_subject_folders(save_path)
                scan_list = list(experiments[session].scans.values())

                T1_idx = [str(x)[-3] for x in scan_list if "t1_" in str(x)]
                if T1_idx != []:
                    T1_idx = T1_idx[0]
                    experiments[session].scans[T1_idx].download(os.path.join(save_path, 'anat/t1.zip'))
                    zip_file = zipfile.ZipFile(os.path.join(save_path, 'anat/t1.zip'))
                    zip_file.extractall(os.path.join(save_path, 'anat'))
                bold_idx = [str(x)[-3] for x in scan_list if "REST_cmrr_mbep2d_bold_mat64_32Ch " in str(x)]
                if bold_idx != []:
                    bold_idx = bold_idx[0]
                    experiments[session].scans[bold_idx].download(os.path.join(save_path, 'func/bold.zip'))
                    zip_file = zipfile.ZipFile(os.path.join(save_path, 'func/bold.zip'))
                    zip_file.extractall(os.path.join(save_path, 'func'))
    _move_files(path)
    return

def parse_arguments():
    '''
        Parses all input arguments for the script. 

        Outputs:
            - args: (dict) Contains all parsed arguments.
    '''
    # parse commandline arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '-I', '--input', required=True, help='Directory to download data to.')
    ap.add_argument('--patient_list', default='all', help='List of patient subject data to be downloaded.')
    ap.add_argument('--control_list', default='all', help='List of control subject data to be downloaded.')
    ap.add_argument('--mode', default='both', choices=['patient', 'control', 'both'], help='Defines whether to download patient data, control data or both.')
    ap.add_argument('-u', '--user', required=True, help='Username for Monash xnat')
    ap.add_argument('-p', '--password', required=True, help='Password for Monash XNAT')
    ap.add_argument('--project_ID', required=True, help='Project ID')
    args = vars(ap.parse_args())

    return args


def main():
    '''
        Main function --> runs everything.
    '''
    args = parse_arguments()

    input_path = args['input']
        
    control_path = os.path.join(input_path, 'controls')
    patient_path = os.path.join(input_path, 'patients')
    patient_list = args['patient_list'].split(',')
    control_list = args['control_list'].split(',')

    mode = args['mode']

    user = args['user']
    pswd = args['password']

    project_ID = args['project_ID']

    session = xnat.connect('https://mbi-xnat.erc.monash.edu.au', user=user, password=pswd)
    project = session.projects[project_ID]
    controls, patients = _get_subject_list(project, patient_list, control_list)

    if mode == 'control':
        print(controls)
        download_data(controls, control_path)	# download control data

    elif mode == 'patient':
        print(patients)
        download_data(patients, patient_path)	# download patient data

    else:
        download_data(controls, control_path)	# download control data
        download_data(patients, patient_path)	# download patient data

    return


if __name__ == "__main__":
    main()

