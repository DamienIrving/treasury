#
# Bash script for processing a model / experiment
#
# Usage: bash run.sh {model} {ssp} {metric} {job} {flags}
#
#   model:   ACCESS-CM2 ACCESS-ESM1-5 MPI-ESM1-2-LR
#   ssp:     ssp126 ssp245 ssp370 ssp585
#   metric:  wsdi spei ffdi rx1day rx5day
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
    default_version=latest
    grid=gn
elif [[ "${model}" == "ACCESS-ESM1-5" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r5i1p1f1" "r6i1p1f1" "r7i1p1f1" "r8i1p1f1" "r9i1p1f1" "r10i1p1f1" "r11i1p1f1" "r12i1p1f1" "r13i1p1f1" "r14i1p1f1" "r15i1p1f1" "r16i1p1f1" "r17i1p1f1" "r18i1p1f1" "r19i1p1f1" "r20i1p1f1" "r21i1p1f1" "r22i1p1f1" "r23i1p1f1" "r24i1p1f1" "r25i1p1f1" "r26i1p1f1" "r27i1p1f1" "r28i1p1f1" "r29i1p1f1" "r30i1p1f1" "r31i1p1f1" "r32i1p1f1" "r33i1p1f1" "r34i1p1f1" "r35i1p1f1" "r36i1p1f1" "r37i1p1f1" "r38i1p1f1" "r39i1p1f1" "r40i1p1f1")
    default_version=latest
    grid=gn
elif [[ "${model}" == "CanESM5" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r5i1p1f1" "r6i1p1f1" "r7i1p1f1" "r8i1p1f1" "r9i1p1f1" "r10i1p1f1" "r11i1p1f1" "r12i1p1f1" "r13i1p1f1" "r14i1p1f1" "r15i1p1f1" "r16i1p1f1" "r17i1p1f1" "r18i1p1f1" "r19i1p1f1" "r20i1p1f1" "r21i1p1f1" "r22i1p1f1" "r23i1p1f1" "r24i1p1f1" "r25i1p1f1" "r1i1p2f1" "r2i1p2f1" "r3i1p2f1" "r4i1p2f1" "r5i1p2f1" "r6i1p2f1" "r7i1p2f1" "r8i1p2f1" "r9i1p2f1" "r10i1p2f1" "r11i1p2f1" "r12i1p2f1" "r13i1p2f1" "r14i1p2f1" "r15i1p2f1" "r16i1p2f1" "r17i1p2f1" "r18i1p2f1" "r19i1p2f1" "r20i1p2f1" "r21i1p2f1" "r22i1p2f1" "r23i1p2f1" "r24i1p2f1" "r25i1p2f1")
    default_version=v20190429
    grid=gn
elif [[ "${model}" == "CMCC-ESM2" ]] ; then
    declare -a runs=("r1i1p1f1")
    default_version="v*"
    grid=gn
elif [[ "${model}" == "CNRM-ESM2-1" ]] ; then
    declare -a runs=("r1i1p1f2")
    default_version="v*"
    grid=gr
elif [[ "${model}" == "EC-Earth3" ]] ; then
    if [[ "${metric}" == "FFDI" ]] ; then
        declare -a runs=("r1i1p1f1")
        default_version="v20200310"
        grid=gr
    else
        declare -a runs=("r1i1p1f1" "r4i1p1f1" "r6i1p1f1" "r9i1p1f1" "r11i1p1f1" "r13i1p1f1" "r15i1p1f1" "r101i1p1f1" "r102i1p1f1" "r103i1p1f1" "r104i1p1f1" "r105i1p1f1" "r106i1p1f1" "r107i1p1f1" "r108i1p1f1" "r109i1p1f1" "r110i1p1f1" "r111i1p1f1" "r112i1p1f1" "r113i1p1f1" "r114i1p1f1" "r115i1p1f1" "r116i1p1f1" "r117i1p1f1" "r118i1p1f1" "r119i1p1f1" "r120i1p1f1" "r121i1p1f1" "r122i1p1f1" "r123i1p1f1" "r124i1p1f1" "r125i1p1f1" "r126i1p1f1" "r127i1p1f1" "r128i1p1f1" "r129i1p1f1" "r130i1p1f1" "r131i1p1f1" "r132i1p1f1" "r133i1p1f1" "r134i1p1f1" "r135i1p1f1" "r136i1p1f1" "r137i1p1f1" "r138i1p1f1" "r139i1p1f1" "r140i1p1f1" "r141i1p1f1" "r142i1p1f1" "r143i1p1f1" "r144i1p1f1" "r145i1p1f1" "r146i1p1f1" "r147i1p1f1" "r148i1p1f1" "r149i1p1f1" "r150i1p1f1")
        default_version="v*"
        grid=gr
        #r9i1p1f1, ssp126: v20200514
    fi
elif [[ "${model}" == "EC-Earth3-Veg" ]] ; then
    if [[ "${metric}" == "FFDI" ]] ; then
        declare -a runs=("r12i1p1f1" "r14i1p1f1")
        default_version="v20200925"
        grid=gr
    else
        declare -a runs=("r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r12i1p1f1" "r14i1p1f1")
        default_version="v*"
        grid=gr
    fi
elif [[ "${model}" == "IPSL-CM6A-LR" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r6i1p1f1" "r14i1p1f1")
    default_version="v*"
    grid=gr
elif [[ "${model}" == "MPI-ESM1-2-LR" ]] ; then
    declare -a runs=("r1i1p1f1" "r2i1p1f1" "r3i1p1f1" "r4i1p1f1" "r5i1p1f1" "r6i1p1f1" "r7i1p1f1" "r8i1p1f1" "r9i1p1f1" "r10i1p1f1")
    default_version="v*"
    grid=gn
elif [[ "${model}" == "UKESM1-0-LL" ]] ; then
    declare -a runs=("r1i1p1f2" "r2i1p1f2" "r3i1p1f2" "r4i1p1f2" "r8i1p1f2")
    default_version="v*"
    grid=gn
    #r41ip1f2, ssp585: v20211201
fi

for run in "${runs[@]}"; do

    if [[ "${model}" == "UKESM1-0-LL" ]] && [[ "${run}" == "r4i1p1f2" ]] && [[ "${ssp}" == "ssp585" ]] ; then
        hversion=${default_version}
        sversion=v20211201
    elif [[ "${model}" == "UKESM1-0-LL" ]] && [[ "${run}" == "r4i1p1f2" ]] && [[ "${ssp}" == "ssp126" ]] ; then
        hversion=${default_version}
        sversion=v20190815
    elif [[ "${model}" == "EC-Earth3" ]] && [[ "${run}" == "r9i1p1f1" ]] && [[ "${ssp}" == "ssp126" ]] ; then
        hversion=${default_version}
        sversion=v20200514
    else
        hversion=${default_version}
        sversion=${default_version}
    fi

    if [[ "${job}" == "test" ]] ; then
        command="bash ${metric}_cmip6.sh ${model} ${ssp} ${run} ${grid} ${hversion} ${sversion}"
    elif [[ "${job}" == "calc" ]] ; then
        command="qsub -v metric=${metric},model=${model},ssp=${ssp},run=${run},grid=${grid},hversion=${hversion},sversion=${sversion} cmip6.job"
    elif [[ "${job}" == "clean" ]] ; then
        command="bash ${metric}_cmip6.sh ${model} ${ssp} ${run} ${grid} ${hversion} ${sversion} -c"
    fi
    if [[ "${flags}" == "-n" ]] ; then
        echo ${command}
    else
        echo ${command}
        ${command}
    fi
done

