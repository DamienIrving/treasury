#
# Bash script for calculating Rx5day from BARRA data
#
# Usage: bash rx5day_barra.sh {flags}
#
#   flags:  optional flags (e.g. -e for execute)
#

flags=$1

python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python

indir=/g/data/ob53/BARRA2/output/reanalysis/AUS-11/BOM/ERA5/historical/hres/BARRA-R2/v1/day
outdir=/g/data/xv83/dbi599/rba/Rx5day/BARRA-R2

for year in $(seq 1980 2024); do
    pr_files=(`ls ${indir}/pr/latest/*_${year}??-??????.nc`)
    nc_outfile=${outdir}/Rx5day_yr_BARRA-R2_AUST-11_${year}.nc
    nc_command="${python} /home/599/dbi599/rba/rx5day.py ${nc_outfile} ${pr_files[@]} --ausclip"
    if [[ "${flags}" == "-e" ]] ; then
        mkdir -p ${outdir}
        echo ${nc_command}
        ${nc_command}
    else
        echo ${nc_command}
    fi
done

nc_files=(`ls ${outdir}/Rx5day_yr_BARRA-R2_AUST-11_????.nc`)
csv_outfile=${outdir}/Rx5day_yr_BARRA-R2_aus-states-cities_1980-2024.csv
csv_command="${python} /home/599/dbi599/rba/nc_to_csv.py ${nc_files[@]} Rx5day ${csv_outfile} --add_cities"
if [[ "${flags}" == "-e" ]] ; then
    echo ${csv_command}
    ${csv_command}
else
    echo ${csv_command}
fi


if [[ "${flags}" == "-c" ]] ; then
    rm ${nc_outfile}
fi


