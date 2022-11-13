#!/bin/bash
set -euo pipefail

# TODO: when does Pulsar remove the active jobs file? Hopefully not until it has sent the final status message...

cluster="$1"
period="${2:-1 day}"

case "$cluster" in
    jetstream_iu)
        user='g2main'
        host='jetstream-iu0.galaxyproject.org'
        active_jobs_dir='/srv/pulsar/main/var/persisted_data/jetstream_iu-active-jobs'
        staging_dir='/jetstream/scratch0/main/jobs'
        ;;
    jetstream_tacc)
        user='g2main'
        host='jetstream-tacc0.galaxyproject.org'
        active_jobs_dir='/srv/pulsar/main/var/persisted_data/jetstream_tacc-active-jobs'
        staging_dir='/jetstream/scratch0/main/jobs'
        ;;
    jetstream2)
        user='g2main'
        host='jetstream2.galaxyproject.org'
        active_jobs_dir='/srv/pulsar/main/var/persisted_data/jetstream2-active-jobs'
        staging_dir='/jetstream2/scratch/main/jobs'
        ;;
    bridges)
        user='xcgalaxy'
        host='vm030.bridges2.psc.edu'
        active_jobs_dir='/ocean/projects/mcb140028p/xcgalaxy/main/pulsar/var/bridges-active-jobs'
        staging_dir='/ocean/projects/mcb140028p/xcgalaxy/main/staging'
        ;;
    expanse)
        user='xgalaxy'
        host='login01.expanse.sdsc.edu'
        active_jobs_dir='/expanse/lustre/scratch/xgalaxy/temp_project/main/pulsar/var/expanse-active-jobs'
        staging_dir='/expanse/lustre/scratch/xgalaxy/temp_project/main/staging'
        ;;
    stampede)
        user='xcgalaxy'
        host='login2.stampede2.tacc.utexas.edu'
        active_jobs_dir='/scratch/03166/xcgalaxy/main/pulsar/var/persisted_data/stampede-active-jobs'
        staging_dir='/scratch/03166/xcgalaxy/main/staging'
        ;;
    frontera)
        user='xcgalaxy'
        host='login4.frontera.tacc.utexas.edu'
        active_jobs_dir='/work2/03166/xcgalaxy/frontera/main/pulsar/var/persisted_data/frontera-active-jobs'
        staging_dir='/scratch1/03166/xcgalaxy/main/staging'
        ;;
    tacc_k8s)
        period="${2:-2 days}"
        ;;
    *)
        echo "usage: $0 <cluster>"
        exit 1
        ;;
esac


function db_nonterminal_jobs() {
    echo "Collecting nonterminal jobs on ${cluster} in DB..." >&2
    #set -x
    gxadmin tsvquery jobs-nonterminal \
        --states=queued,running --update-time --older-than="$period" \
        | grep "$cluster" | awk '{print $1}' | sort -n
    { set +x; }; 2>/dev/null
}


function pulsar_nonterminal_jobs() {
    echo "Collecting nonterminal jobs on ${cluster} in Pulsar..." >&2
    ssh -l "$user" "$host" /bin/ls -1 "$active_jobs_dir" | sort -n
}


function clean_lost_pulsar_jobs() {
    echo "Removing lost Pulsar job dirs on ${cluster}..." >&2
    cat lost_jobs | sed "s#^#${staging_dir}/#" | xargs ssh -l "$user" "$host" rm -rf
    cat lost_jobs | sed "s#^#${active_jobs_dir}/#" | xargs ssh -l "$user" "$host" rm -f
}


function requeue_lost_pulsar_jobs() {
    echo "Requeueing lost jobs in Galaxy"
    #for job_id in $(cat lost_jobs); do
    #    ssh -l g2main galaxy-web-05 /home/g2main/bin/helper --requeue-job=$job_id --commit
    #done
    cat lost_jobs | ssh -l g2main galaxy-db-02 /home/g2main/bin/gxadmin-local mutate restart-jobs --commit -
}


case "$cluster" in
    tacc_k8s)
        for job_id in $(db_nonterminal_jobs); do
            echo "Failing lost job ${job_id} in Galaxy"
            ssh -l g2main galaxy-web-05 /home/g2main/bin/helper --failjob=$job_id --commit
        done
        exit 0
        ;;
esac


workdir=$(mktemp -p /tmp -d fix-lost-pulsar-jobs.XXXXXXXX)

cd "$workdir"
echo "Workdir is ${workdir}"

db_nonterminal_jobs > 'db_nonterminal_jobs'
pulsar_nonterminal_jobs > 'pulsar_nonterminal_jobs'

comm -23 'db_nonterminal_jobs' 'pulsar_nonterminal_jobs' > 'lost_jobs'

if [ $(stat --printf=%s 'lost_jobs') -ne 0 ]; then
    cat 'lost_jobs' | xargs echo "Found lost jobs: "
    clean_lost_pulsar_jobs
    requeue_lost_pulsar_jobs
else
    echo "No lost jobs"
fi

cd "$HOME"
rm -rf "$workdir"
