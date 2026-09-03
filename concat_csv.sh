#
# Bash script for concatenating csv files
#
# Usage: bash concat_csv.sh {model} {ssp} {metric} {flags}
#
#   model:   ACCESS-CM2 ACCESS-ESM1-5 MPI-ESM1-2-LR
#   ssp:     ssp126 ssp245 ssp370 ssp585
#   metric:  wsdi spei ffdi rx1day rx5day
#   flags:   optional flags (e.g. -n for dry run)
#

model=$1
ssp=$2
metric=$3
flags=$4


python=/g/data/xv83/dbi599/miniconda3/envs/unseen/bin/python

if [[ "${metric}" == "rx5day" ]] ; then
    dir_metric=Rx5day
    like_metric=Rx5day
    file_metric=rx5day
    locations=aus-states-cities
    tscale=yr
elif [[ "${metric}" == "rx1day" ]] ; then
    dir_metric=Rx1day
    like_metric=Rx1day
    file_metric=rx1day
    locations=aus-states-cities
    tscale=yr
elif [[ "${metric}" == "ffdi" ]] ; then
    dir_metric=FFDI
    like_metric=FFDIgt99p
    file_metric=FFDIgt99p
    locations=aus-states
    tscale=yr
elif [[ "${metric}" == "spei" ]] ; then
    dir_metric=SPEI
    like_metric=SPEI
    file_metric=spei
    locations=aus-states
    tscale=mon
elif [[ "${metric}" == "wsdi" ]] ; then
    dir_metric=WSDI
    like_metric=WSDI
    file_metric=wsdi
    locations=aus-states-cities
    tscale=yr
fi

data_dir=/g/data/xv83/dbi599/rba/${dir_metric}/${model}/${ssp}
infiles=(`ls ${data_dir}/${metric}_${tscale}_${model}_${ssp}_r*_${locations}_1850-2100.csv`)
outfile=${data_dir}/${metric}_${tscale}_${model}_${ssp}_ensemble_${locations}_1850-2100.csv

command1="${python} concat_csv.py ${infiles[@]} ${outfile}"
command2="${python} likelihoods.py ${outfile} ${like_metric} ${data_dir}"

if [[ "${flags}" == "-n" ]] ; then
    echo ${command1}
    echo ${command2}
else
    echo ${command1}
    ${command1}
    echo ${command2}
    ${command2}
fi
