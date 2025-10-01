#
# Bash script for calculating the Keetch-Byram Drought Index (KBDI)
#
# Usage: bash kbdi.sh {precip files}

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python

# Calculate annual precipitation climatology

model=`basename $1 | cut -d _ -f 3`
exp=`basename $1 | cut -d _ -f 4`
run=`basename $1 | cut -d _ -f 5`
grid=`basename $1 | cut -d _ -f 6`
pr_clim_path=/g/data/xv83/dbi599/treasury/pr_yr-climatology_${model}_${exp}_${run}_${grid}_1950-2014.nc

clim_command="${python} pr_climatology.py $@ 1950-01-01 2014-12-31 ${pr_clim_path}"
echo ${clim_command}
${clim_command}

# Calculate KBDI

for pr_path in "$@"; do
    tasmax_path=`echo ${pr_path} | sed s:pr:tasmax:g`
    kbdi_file=`basename ${pr_path} | sed s:pr:kbdi:g`
    kbdi_path=/g/data/xv83/dbi599/treasury/${kbdi_file}
    command="${python} kbdi.py ${pr_path} ${tasmax_path} ${pr_clim_path} ${kbdi_path}" 
    echo ${command}
   ${command}   
done

