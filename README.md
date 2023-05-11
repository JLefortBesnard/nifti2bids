# nifti2bids

Create a BIDS formatted directory with a symlink to the required nii files (already converted from DICOM) 
The BIDS directory will contain symlink from the nii files to save space.
Paths must be adapted.

This script is specific for directory with

    -3D Sag T1 MPRAGE
    -3D Sag T2 FLAIR Cube
    -fMRI PA
    -fMRI AP flip polarity
    -Ax DWI HARDI 96dir PA
    -Ax DWI HARDI 6dir AP flip polarity
    -3D Ax ASL PLD 1525
    -CBF

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

        Mikael Naveau 
        Jeremy Lefort-Besnard 
        2021
