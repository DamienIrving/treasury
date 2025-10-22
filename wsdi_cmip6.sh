#
# Bash script for calculating WDSI from CMIP6 data
#
# Usage: bash wsdi_cmip6.sh {model} {ssp} {run} {grid} {version} {flags}
#
#   model:           ACCESS-ESM1-5
#   ssp:             ssp126 ssp245 ssp370 ssp585
#   run:             r?i?p?i?
#   grid:            gn
#   flags:           optional flags (e.g. -n for dry run)
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
outfile=wsdi_yr_${model}_${ssp}_${run}_${grid}_18500101-21001231.nc
    
command="${python} /home/599/dbi599/treasury/wsdi.py ${histfiles[@]} ${sspfiles[@]} ${outdir}/${outfile}"
if [[ "${flags}" == "-n" ]] ; then
    echo ${command}
else
    mkdir -p ${outdir}
    ${command}
    echo ${outdir}/${outfile}
fi







