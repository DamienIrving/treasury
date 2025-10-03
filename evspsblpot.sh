#
# Bash script for calculating potential evapotranspiration
#
# Usage: bash evspsblpot.sh {tasmin files}

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python
for tasmin_path in "$@"; do
    tasmax_path=`echo ${tasmin_path} | sed s:tasmin:tasmax:g`
    hurs_path=`echo ${tasmin_path} | sed s:tasmin:hurs:g`
    sfcwind_path=`echo ${tasmin_path} | sed s:tasmin:sfcWind:g`
    rsds_path=`echo ${tasmin_path} | sed s:tasmin:rsds:g`
    rsus_path=`echo ${tasmin_path} | sed s:tasmin:rsus:g`
    rlds_path=`echo ${tasmin_path} | sed s:tasmin:rlds:g`
    rlus_path=`echo ${tasmin_path} | sed s:tasmin:rlus:g`
    evspsblpot_file=`basename ${tasmin_path} | sed s:tasmin:evspsblpot-allen98:g`
    evspsblpot_path=/g/data/xv83/dbi599/treasury/${evspsblpot_file}
    command="${python} evspsblpot.py ${evspsblpot_path} allen98 --tasmin_file ${tasmin_path} --tasmax_file ${tasmax_path} --hurs_file ${hurs_path} --sfcWind_file ${sfcwind_path} --rsds_file ${rsds_path} --rsus_file ${rsus_path} --rlds_file ${rlds_path} --rlus_file ${rlus_path}" 
    echo ${command}
   ${command}   
done


