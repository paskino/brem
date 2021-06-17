
import brem

from time import sleep
#a=drx.DVCRem(private_key="/home/drFaustroll/.ssh/id_routers")

a = brem.BasicRemoteExecutionManager(host="scarf.rl.ac.uk",username="scarf595",port=22,private_key="C:/Apps/cygwin64/home/ofn77899/.ssh/id_rsa")

a.login(passphrase=False)

#a.generate_keys()
#a.authorize_key('mykey-rsa.pub')
#a.changedir('.')
#print(a.listdir())
inp="input.dvc"
folder="/work3/cse/dvc/test-edo"
datafolder="/work3/cse/dvc/test_data"

with open(inp,'w', newline='\n') as f:
    print("""###############################################################################
#
#
#               example dvc process control file
#
#
###############################################################################

# all lines beginning with a # character are ignored
# some parameters are conditionally required, depending on the setting of other parameters
# for example, if subvol_thresh is off, the threshold description parameters are not required

### file names

reference_filename\t{0}/frame_000_f.npy\t### reference tomography image volume
correlate_filename\t{0}/frame_010_f.npy\t### correlation tomography image volume

point_cloud_filename\t{1}/small_grid.roi\t### file of search point locations
output_filename\t{1}/small_grid\t### base name for output files

### description of the image data files, all must be the same size and structure

vol_bit_depth           8                       ### 8 or 16
vol_hdr_lngth           96                      ### fixed-length header size, may be zero
vol_wide                1520                    ### width in pixels of each slice
vol_high                1257                    ### height in pixels of each slice
vol_tall                1260                    ### number of slices in the stack

### parameters defining the subvolumes that will be created at each search point

subvol_geom             sphere                  ### cube, sphere
subvol_size             80                      ### side length or diameter, in voxels
subvol_npts             8000                    ### number of points to distribute within the subvol

subvol_thresh           off                     ### on or off, evaluate subvolumes based on threshold
#   gray_thresh_min     27                      ### lower limit of a gray threshold range if subvol_thresh is on
#   gray_thresh_max     127                     ### upper limit of a gray threshold range if subvol_thresh is on
#   min_vol_fract       0.2                     ### only search if subvol fraction is greater than

### required parameters defining the basic the search process

disp_max                38                      ### in voxels, used for range checking and global search limits
num_srch_dof            6                       ### 3, 6, or 12
obj_function            znssd                   ### sad, ssd, zssd, nssd, znssd
interp_type             tricubic                ### trilinear, tricubic

### optional parameters tuning and refining the search process

rigid_trans             34.0 4.0 0.0            ### rigid body offset of target volume, in voxels
basin_radius            0.0                     ### coarse-search resolution, in voxels, 0.0 = none
subvol_aspect           1.0 1.0 1.0             ### subvolume aspect ratio



""".format(datafolder,folder),file=f)

a.changedir(folder)
a.put_file(inp)


job="""

module purge
module load AMDmodules foss/2019b

/work3/cse/dvc/codes/CCPi-DVC/build-amd/Core/dvc {0} > {1}
#{0}
""".format(inp, folder+'/dvc.out')



jobid = a.submit_job(folder,job)
print(jobid)
status = a.job_status(jobid)
print(status)
while status in [b'PENDING',b'RUNNING']:
    if status == b'PENDING':
        print("job is queueing")
    else:
        print("job is running")
        # should tail the file in folder+'/dvc.out'
    sleep(20)
    status = a.job_status(jobid)

print("retrieve output for job {}".format(jobid))
a.changedir(folder)
a.get_file("slurm-{}.out".format(jobid))
# here we should fetch also all the output files defined at
# output_filename\t{1}/small_grid\t### base name for output files

a.logout()


