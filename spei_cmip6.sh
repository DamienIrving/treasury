#
# Bash script for calculating SPEI from CMIP6 data
#
# Usage: bash spei_cmip6.sh {model} {ssp} {run} {grid} {version} {flags}
#
#   model:           ACCESS-ESM1-5
#   ssp:             ssp126 ssp245 ssp370 ssp585
#   run:             r?i?p?i?
#   grid:            gn
#   version:         vYYYYMMDD
#   flags:           optional flags (e.g. -e for execute; -c for clean up)
#

model=$1
ssp=$2
run=$3
grid=$4
version=$5
flags=$6

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python

if [[ "${model}" == "ACCESS-ESM1-5" ]] ; then
    indir=/g/data/fs38/publications
elif [[ "${model}" == "ACCESS-CM2" ]] ; then
    indir=/g/data/fs38/publications
else
    indir=/g/data/oi10/replicas
fi
spei_dir=/g/data/xv83/dbi599/treasury/SPEI/${model}/${ssp}

# Potential evapotranspiration (evspsblpot)

tasmin_hist_files=(`ls ${indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/tasmin/${grid}/${version}/*.nc`)
tasmin_ssp_files=(`ls ${indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/tasmin/${grid}/${version}/*.nc`)
tasmin_files=( "${tasmin_hist_files[@]}" "${tasmin_ssp_files[@]}" )
method=hargreaves85
evspsblpot_files=()
for tasmin_path in "${tasmin_files[@]}"; do
    tasmax_path=`echo ${tasmin_path} | sed s:tasmin:tasmax:g`
    evspsblpot_file=`basename ${tasmin_path} | sed s:tasmin:evspsblpot-${method}:g`
    evspsblpot_path=${spei_dir}/${evspsblpot_file}
    evspsblpot_files+=(${evspsblpot_path})
    command="${python} /home/599/dbi599/treasury/evspsblpot.py ${evspsblpot_path} ${method} --tasmin_file ${tasmin_path} --tasmax_file ${tasmax_path}"
    if [[ "${flags}" == "-e" ]] ; then
        mkdir -p ${spei_dir}
        echo ${command}
        ${command}
    else
        echo ${command}
    fi 
done

# SPEI

pr_hist_files=(`ls ${indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/pr/${grid}/${version}/*.nc`)
pr_ssp_files=(`ls ${indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/pr/${grid}/${version}/*.nc`)
spei_path=${spei_dir}/spei_mon_${model}_${ssp}_${run}_${grid}_1850-2100.nc
csv_path=${spei_dir}/spei_mon_${model}_${ssp}_${run}_aus-states_1850-2100.csv

spei_command="${python} /home/599/dbi599/treasury/spei.py ${spei_path} --dist fisk --pr_files ${pr_hist_files[@]} ${pr_ssp_files[@]} --evspsblpot_files ${evspsblpot_files[@]}"
csv_command="${python} /home/599/dbi599/treasury/nc_to_csv.py ${spei_path} SPEI ${csv_path}"
if [[ "${flags}" == "-e" ]] ; then
    echo ${spei_command}
    ${spei_command}
    echo ${csv_command}
    ${csv_command}
else
    echo ${spei_command}
    echo ${csv_command}
fi

if [[ "${flags}" == "-c" ]] ; then
    rm ${evspsblpot_files[@]}
    rm ${spei_path}
fi

