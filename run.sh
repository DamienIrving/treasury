#
# Bash script for processing a model / experiment
#
# Usage: bash run.sh {model} {ssp} {metric} {job} {flags}
#
#   model:   ACCESS-CM2 MPI-ESM1-2-LR
#   ssp:     ssp126 ssp245 ssp370 ssp585
#   metric:  wsdi spei ffdi
#   job:     test calc clean
#   flags:   optional flags (e.g. -n for dry run)
#

model=$1
ssp=$2
metric=$3
job=$4
flags=$5


if [[ "${model}" == "ACCESS-CM2" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r5i1p1f1" "r6i1p1f1" "r7i1p1f1" "r8i1p1f1" "r9i1p1f1" "r10i1p1f1")
    version=latest
    grid=gn
elif [[ "${model}" == "MPI-ESM1-2-LR" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r5i1p1f1" "r6i1p1f1" "r7i1p1f1" "r8i1p1f1" "r9i1p1f1" "r10i1p1f1" "r14i1p1f1" "r15i1p1f1" "r25i1p1f1")
    version="v*"
    grid=gn
fi

for run in "${runs[@]}"; do
    if [[ "${job}" == "test" ]] ; then
        command="bash ${metric}_cmip6.sh ${model} ${ssp} ${run} ${grid} ${version}"
    elif [[ "${job}" == "calc" ]] ; then
        command="qsub -v metric=${metric},model=${model},ssp=${ssp},run=${run},grid=${grid},version=${version} cmip6.job"
    elif [[ "${job}" == "clean" ]] ; then
        command="bash ${metric}_cmip6.sh ${model} ${ssp} ${run} ${grid} ${version} -c"
    fi
    if [[ "${flags}" == "-n" ]] ; then
        echo ${command}
    else
        echo ${command}
        ${command}
    fi
done






