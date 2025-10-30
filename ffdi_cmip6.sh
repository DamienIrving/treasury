#
# Bash script for calculating FFDI from CMIP6 data
#
# Usage: bash ffdi_cmip6.sh {model} {ssp} {run} {grid} {version} {flags}
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
ffdi_dir=/g/data/xv83/dbi599/treasury/FFDI/${model}/${ssp}

# Keetch-Byram Drought Index (KBDI)

pr_hist_files=(`ls ${indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/pr/${grid}/${version}/*.nc`)
pr_ssp_files=(`ls ${indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/pr/${grid}/${version}/*.nc`)
pr_files=( "${pr_hist_files[@]}" "${pr_ssp_files[@]}" )

pr_clim_path=/g/data/xv83/dbi599/treasury/pr_yr-climatology_${model}_historical_${run}_${grid}_1950-2014.nc
pr_clim_command="${python} /home/599/dbi599/treasury/pr_climatology.py ${pr_hist_files[@]} 1950-01-01 2014-12-31 ${pr_clim_path}"
if [[ "${flags}" == "-e" ]] ; then
    mkdir -p ${ffdi_dir}
    echo ${pr_clim_command}
    ${pr_clim_command}
else
    echo ${pr_clim_command}
fi

kbdi_files=()
for pr_path in "${pr_files[@]}"; do
    tasmax_path=`echo ${pr_path} | sed s:pr:tasmax:g`
    kbdi_file=`basename ${pr_path} | sed s:pr:kbdi:g`
    kbdi_path=${ffdi_dir}/${kbdi_file}
    kbdi_files+=(${kbdi_path})
    kbdi_command="${python} /home/599/dbi599/treasury/kbdi.py ${pr_path} ${tasmax_path} ${pr_clim_path} ${kbdi_path}"
    if [[ "${flags}" == "-e" ]] ; then
        echo ${kbdi_command}
        ${kbdi_command}
    else
        echo ${kbdi_command}
    fi 
done

# Zarr

for var in pr tasmax hursmin sfcWindmax; do
    hist_files=(`ls ${indir}/CMIP6/CMIP/*/${model}/historical/${run}/day/${var}/${grid}/${version}/*.nc`)
    ssp_files=(`ls ${indir}/CMIP6/ScenarioMIP/*/${model}/${ssp}/${run}/day/${var}/${grid}/${version}/*.nc`)
    hist_dates=`basename "${hist_files[0]}" | cut -d _ -f 7`
    start_date=`echo ${hist_dates} | cut -d - -f 1`
    ssp_dates=`basename "${ssp_files[-1]}" | cut -d _ -f 7`
    end_date=`echo ${ssp_dates} | cut -d - -f 2`
    end_date=`echo ${end_date} | cut -d . -f 1`
    zarr_file=${ffdi_dir}/${var}_day_${model}_${ssp}_${run}_${grid}_${start_date}-${end_date}.zarr
    declare ${var}_zarr_file=${zarr_file}
    zarr_command="/g/data/xv83/dbi599/miniconda3/envs/agcd/bin/python /home/599/dbi599/treasury/nc_to_rechunked_zarr.py ${hist_files[@]} ${ssp_files[@]} ${var} ${zarr_file} /g/data/xv83/dbi599/treasury/temp.zarr"
    if [[ "${flags}" == "-e" ]] ; then
        echo ${zarr_command}
        ${zarr_command}
        rm -r /g/data/xv83/dbi599/treasury/temp.zarr
    else
        echo ${zarr_command}
    fi
done

# FFDI

FFDIx_nc_path=${ffdi_dir}/FFDIx_yr_${model}_${ssp}_${run}_${grid}_1850-2100.nc
FFDIgt99p_nc_path=${ffdi_dir}/FFDIgt99p_yr_${model}_${ssp}_${run}_${grid}_1850-2100.nc
FFDIx_csv_path=${ffdi_dir}/FFDIx_yr_${model}_${ssp}_${run}_aus-states_1850-2100.csv
FFDIgt99p_csv_path=${ffdi_dir}/FFDIgt99p_yr_${model}_${ssp}_${run}_aus-states_1850-2100.csv

ffdi_command="${python} /home/599/dbi599/treasury/ffdi.py ${FFDIx_nc_path} ${FFDIgt99p_nc_path} --pr_zarr ${pr_zarr_file} --tasmax_zarr ${tasmax_zarr_file} --hursmin_zarr ${hursmin_zarr_file} --sfcWindmax_zarr ${sfcWindmax_zarr_file} --kbdi_files ${kbdi_files[@]}"
FFDIx_csv_command="${python} /home/599/dbi599/treasury/nc_to_csv.py ${FFDIx_nc_path} FFDIx ${FFDIx_csv_path} --mask_arid"
FFDIgt99p_csv_command="${python} /home/599/dbi599/treasury/nc_to_csv.py ${FFDIgt99p_nc_path} FFDIgt99p ${FFDIgt99p_csv_path} --mask_arid"
if [[ "${flags}" == "-e" ]] ; then
    echo ${ffdi_command}
    ${ffdi_command}
    echo ${FFDIx_csv_command}
    ${FFDIx_csv_command}
    echo ${FFDIgt99p_csv_command}
    ${FFDIgt99p_csv_command}
else
    echo ${ffdi_command}
    echo ${FFDIx_csv_command}
    echo ${FFDIgt99p_csv_command}
fi

# Clean up

if [[ "${flags}" == "-c" ]] ; then
    rm ${pr_clim_path}
    rm ${kbdi_files[@]}
    rm -r ${pr_zarr_file}
    rm -r ${tasmax_zarr_file}
    rm -r ${hursmin_zarr_file}
    rm -r ${sfcWindmax_zarr_file}
fi


