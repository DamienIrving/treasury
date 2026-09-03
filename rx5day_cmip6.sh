#
# Bash script for calculating Rx5day from CMIP6 data
#
# Usage: bash rx5day_cmip6.sh {model} {ssp} {run} {grid} {version} {flags}
#
#   model:           ACCESS-ESM1-5
#   ssp:             ssp126 ssp245 ssp370 ssp585
#   run:             r?i?p?i?
#   grid:            gn
#   hversion:        historical experiment version (vYYYYMMDD or 'v*')
#   sversion:        ssp experiment version (vYYYYMMDD or 'v*')
#   flags:           optional flags (e.g. -e for execute; -c for clean up)
#

model=$1
ssp=$2
run=$3
grid=$4
hversion=$5
sversion=$6
flags=$7

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python

if [[ "${model}" == "ACCESS-ESM1-5" ]] ; then
    pr_indir=/g/data/fs38/publications
elif [[ "${model}" == "ACCESS-CM2" ]] ; then
    pr_indir=/g/data/fs38/publications
else
    pr_indir=/g/data/oi10/replicas
fi
rx5day_dir=/g/data/xv83/dbi599/rba/Rx5day/${model}/${ssp}

pr_hist_files=(`ls ${pr_indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/pr/${grid}/${hversion}/*.nc`)
pr_ssp_files=(`ls ${pr_indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/pr/${grid}/${sversion}/*20??????-????????.nc`)
rx5day_path=${rx5day_dir}/rx5day_yr_${model}_${ssp}_${run}_${grid}_1850-2100.nc
csv_path=${rx5day_dir}/rx5day_yr_${model}_${ssp}_${run}_aus-states-cities_1850-2100.csv

rx5day_command="${python} /home/599/dbi599/rba/rx5day.py ${rx5day_path} ${pr_hist_files[@]} ${pr_ssp_files[@]}"
csv_command="${python} /home/599/dbi599/rba/nc_to_csv.py ${rx5day_path} Rx5day ${csv_path} --add_cities"
if [[ "${flags}" == "-e" ]] ; then
    mkdir -p ${rx5day_dir}
    echo ${rx5day_command}
    ${rx5day_command}
    echo ${csv_command}
    ${csv_command}
else
    echo ${rx5day_command}
    echo ${csv_command}
fi

if [[ "${flags}" == "-c" ]] ; then
    rm ${rx5day_path}
    rm ${csv_path}
else
    echo rm ${rx5day_path}
    echo rm ${csv_path}
fi

