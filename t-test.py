import argparse
import os
import numpy as np
import nibabel as nib
from scipy import stats

# parse commandline arguments
ap = argparse.ArgumentParser()
ap.add_argument('--group1', required=True, help='Group 1 text file containing list of group 1 files.')
ap.add_argument('--group2', required=True, help='Group 2 text file containing list of group 2 files.')
ap.add_argument('--group1_comp', required=True, help='Component number of group 1')
ap.add_argument('--group2_comp', required=True, help='Component number of group 2')
ap.add_argument('-i', '--independent', default=True, help='To use the independent or paired t-test')
args = vars(ap.parse_args())

group1Files = args['group1']
group1Comp = args['group1_comp']
group2Files = args['group2']
group2Comp = args['group2_comp']

independent = eval(args['independent'])

group1Comp = group1Comp.split(' ') 
group2Comp = group2Comp.split(' ')

#print(group1Comp, group2Comp)

# loops through each pair of components
for idx in range(len(group1Comp)):
        # get means and counts for group 1       
        group1Means = []
        group1Counts = []
        with open(group1Files) as f:
            for i, line in enumerate(f):
                line = line.strip('\n')
        	# read nifti file with components
                im = nib.load(line)
                # convert to numpy
                data = np.array(im.dataobj)[:,:,:,int(group1Comp[idx])]
                # threshold between 2 and 6
                data = np.where((data<2) | (data >6), 0, data)
                # append cluster size
                group1Counts.append(np.count_nonzero(data))
                # append means
                group1Means.append(np.mean(data[data>0]))
        #print(group1Counts, group1Means)
        
        # get means and counts for group 3
        group2Means = []
        group2Counts = []
        with open(group2Files) as f:
            for i, line in enumerate(f):
                line = line.strip('\n')
        	# read nifti file with components
                im = nib.load(line)
                # convert to numpy
                data = np.array(im.dataobj)[:,:,:,int(group2Comp[idx])]
                # threshold between 2 and 6
                data = np.where((data<2) | (data >6), 0, data)
        		# append cluster size 
                group2Counts.append(np.count_nonzero(data))
                # append means
                group2Means.append(np.mean(data[data>0]))
        #print(group2Counts, group2Means)
        
        if independent:
            # perform independent t-Test
            stat, p = stats.ttest_ind(group1Means, group2Means)
            print('Performing independent t-Test\n')
        else:
            # perform paired t-Test
            stat, p = stats.ttest_rel(group1Means, group2Means)
            print('Performing paired t-Test\n')

        print('Group 1 component: {}, Group 2 component: {}\nP={:f}\nCluster sizes:\nGroup 1={:.2f}, Group 2 {:.2f}\n'.format(group1Comp[idx], group2Comp[idx], p, np.mean(group1Counts), np.mean(group2Counts)))
        


