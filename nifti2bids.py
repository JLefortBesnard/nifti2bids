"""
Create a BIDS formatted directory with a symlink to the required nii files (already converted from DICOM) 
The BIDS directory will contain symlink from the nii files to save space.
Paths must be adapted.

This script is specific for directory with
    3D Sag T1 MPRAGE
    3D Sag T2 FLAIR Cube
    fMRI PA
    fMRI AP flip polarity
    Ax DWI HARDI 96dir PA
    Ax DWI HARDI 6dir AP flip polarity
    3D Ax ASL PLD 1525
    CBF

You end up with this type of directory architecture:
    BIDS/sub-1/anat/sub-1_T1w
                   /sub-1_FLAIR
              /func/sub-1_task-rest_bold
                    sub-1_task-rest_bold.nii.gz
              /dwi/sub-1_dwi
                  /sub-1_dwi.bval
                  /sub-1_dwi.bvec
                  /sub-1_dwi.nii.gz
              /fmap/sub-1_acq-GE_dir-AP_epi
                   /sub-1_acq-SE_dir-AP_epi
              /perf/sub-1_m0scan
                   /sub-1_deltam
                   /sub-1_cbf

        /sub-2/...


Authors:
        Mikael Naveau mikael (dot) naveau (at) cyceron (dot) fr
        Jeremy Lefort-Besnard   jlefortbesnard (at) tuta (dot) io
        2021
"""

from glob import glob
import json
import os
from os import symlink
import nibabel as nib
import sys

# run the script from the terminal with 'mri session' and 'subject' as 1st and 2nd argument
mri_session=sys.argv[1]
subject=sys.argv[2]

# path to raw nii files
dcm2niix_reldir='../../../DCM2NIIX/{}'.format(mri_session)

# create BIDS formated directories
os.mkdir('BIDS/sub-{}'.format(subject))
os.mkdir('BIDS/sub-{}/anat'.format(subject))
os.mkdir('BIDS/sub-{}/func'.format(subject))
os.mkdir('BIDS/sub-{}/dwi'.format(subject))
os.mkdir('BIDS/sub-{}/fmap'.format(subject))
os.mkdir('BIDS/sub-{}/perf'.format(subject))

for json_file in glob('DCM2NIIX/{}/*.json'.format(mri_session)):
    (p, filename) = os.path.split(json_file)
    json_target = '{}/{}'.format(dcm2niix_reldir, filename)
    nifti_target = '{}/{}'.format(dcm2niix_reldir, filename.replace('.json', '.nii.gz'))
    with open(json_file, 'r') as f:
        bids_info = json.load(f)

    if bids_info['SeriesDescription'] == '3D Sag T1 MPRAGE':
        basename = 'BIDS/sub-{subject}/anat/sub-{subject}_T1w'.format(subject=subject)
        symlink(json_target, basename + '.json')
        symlink(nifti_target, basename + '.nii.gz')

    if bids_info['SeriesDescription'] == '3D Sag T2 FLAIR Cube':
        basename = 'BIDS/sub-{subject}/anat/sub-{subject}_FLAIR'.format(subject=subject)
        symlink(json_target, basename + '.json')
        symlink(nifti_target, basename + '.nii.gz')

    if bids_info['SeriesDescription'] == 'fMRI PA':
        basename = 'BIDS/sub-{subject}/func/sub-{subject}_task-rest_bold'.format(subject=subject)
        # Add task to the json file
        bids_info['TaskName'] = 'rest'
        with open(basename + '.json', 'w') as f:
            json.dump(bids_info, f, sort_keys=True, indent=4)
        symlink(nifti_target, basename + '.nii.gz')

    if bids_info['SeriesDescription'] == 'fMRI AP flip polarity':
        basename = 'BIDS/sub-{subject}/fmap/sub-{subject}_acq-GE_dir-AP_epi'.format(subject=subject)
        # Add link to the rest acquisition to the json file
        bids_info['IntendedFor'] = 'func/sub-{subject}_task-rest_bold.nii.gz'.format(subject=subject)
        with open(basename + '.json', 'w') as f:
            json.dump(bids_info, f, sort_keys=True, indent=4)
        symlink(nifti_target, basename + '.nii.gz')


    if bids_info['SeriesDescription'] == 'Ax DWI HARDI 96dir PA':
        basename = 'BIDS/sub-{subject}/dwi/sub-{subject}_dwi'.format(subject=subject)
        symlink(json_target, basename + '.json')
        symlink(nifti_target, basename + '.nii.gz')
        symlink(json_target.replace('.json', '.bval'), basename + '.bval')
        symlink(json_target.replace('.json', '.bvec'), basename + '.bvec')

    if bids_info['SeriesDescription'] == 'Ax DWI HARDI 6dir AP flip polarity':
        basename = 'BIDS/sub-{subject}/fmap/sub-{subject}_acq-SE_dir-AP_epi'.format(subject=subject)
        # Add link to the rest acquisition to the json file
        bids_info['IntendedFor'] = 'dwi/sub-{subject}_dwi.nii.gz'.format(subject=subject)
        with open(basename + '.json', 'w') as f:
            json.dump(bids_info, f, sort_keys=True, indent=4)
        # Only keep the first b=0s/mm2 volumes
        bvals_file = json_file.replace('.json', '.bval')
        with open(bvals_file, 'r') as f:
            line = f.readline()
            bvals = line.split()
        nii_list = nib.funcs.four_to_three(nib.load(json_file.replace('.json', '.nii.gz')))
        b0_volumes = [nii for (nii,b) in zip(nii_list, bvals) if b=='0']
        nib.save(nib.funcs.concat_images(b0_volumes), basename + '.nii.gz')

    if bids_info['SeriesDescription'] == '3D Ax ASL PLD 1525':
        if bids_info['ImageType'][0] == 'ORIGINAL':
            basename = 'BIDS/sub-{subject}/perf/sub-{subject}_m0scan'.format(subject=subject)
            symlink(json_target, basename + '.json')
            symlink(nifti_target, basename + '.nii.gz')
        if bids_info['ImageType'][0] == 'DERIVED':
            basename = 'BIDS/sub-{subject}/perf/sub-{subject}_deltam'.format(subject=subject)
            symlink(json_target, basename + '.json')
            symlink(nifti_target, basename + '.nii.gz')

    if bids_info['SeriesDescription'] == 'CBF':
        basename = 'BIDS/sub-{subject}/perf/sub-{subject}_cbf'.format(subject=subject)
        symlink(json_target, basename + '.json')
        symlink(nifti_target, basename + '.nii.gz')
