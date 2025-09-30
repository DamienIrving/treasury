#
# Bash script for calculating potential evapotranspiration
#
# Usage: bash evspsblpot.sh {tasmin files}

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python
for tasmin_path in "$@"; do
    tasmax_path=`echo ${tasmin_path} | sed s:tasmin:tasmax:g`
    evspsblpot_file=`basename ${tasmin_path} | sed s:tasmin:evspsblpot:g`
    evspsblpot_path=/g/data/xv83/dbi599/treasury/${evspsblpot_file}
    command="${python} evspsblpot.py ${tasmin_path} ${tasmax_path} ${evspsblpot_path}" 
    echo ${command}
   ${command}   
done


