#
# Bash script for calculating WDSI from CMIP6 data
#
# Usage: bash wsdi_cmip6.sh {model} {ssp} {run} {grid} {version} {flags}
#
#   model:           ACCESS-ESM1-5
#   ssp:             ssp126 ssp245 ssp370 ssp585
#   run:             r?i?p?i?
#   grid:            gn
#   version:         vYYYYMMDD or 'v*'
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
outdir=/g/data/xv83/dbi599/treasury/WSDI/${model}/${ssp}

histfiles=(`ls ${indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/tasmax/${grid}/${version}/*.nc`)
sspfiles=(`ls ${indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/tasmax/${grid}/${version}/*.nc`)
nc_outfile=wsdi_yr_${model}_${ssp}_${run}_${grid}_1850-2100.nc
csv_outfile=wsdi_yr_${model}_${ssp}_${run}_aus-states-cities_1850-2100.csv
    
nc_command="${python} /home/599/dbi599/treasury/wsdi.py ${histfiles[@]} ${sspfiles[@]} ${outdir}/${nc_outfile}"
csv_command="${python} /home/599/dbi599/treasury/nc_to_csv.py ${outdir}/${nc_outfile} WSDI ${outdir}/${csv_outfile} --add_cities"
if [[ "${flags}" == "-e" ]] ; then
    mkdir -p ${outdir}
    echo ${nc_command}
    ${nc_command}
    echo ${csv_command}
    ${csv_command}
else
    echo ${nc_command}
    echo ${csv_command}
fi

if [[ "${flags}" == "-c" ]] ; then
    rm ${nc_outfile}
fi







