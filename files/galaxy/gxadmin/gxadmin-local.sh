# This file is managed by ansible.  Do not edit it directly
# To add extra local functions, make a PR with usegalaxy-au/infrastructure
# or create a file ~/.config/gxadmin-local-extra.sh

GXADMIN_LOCAL_EXTRA=${BASH_SOURCE%/*}/gxadmin-local-extra.sh
[ -f $GXADMIN_LOCAL_EXTRA ] && source $GXADMIN_LOCAL_EXTRA

registered_subcommands="$registered_subcommands local"

local_query-monthly-users-registered-by-group(){ ## [year]: Number of users registered each month for each group
	handle_help "$@" <<-EOF
        Number of users per group each month that registered. **NOTE**: Does not include anonymous users or users in no group.

        $ gxadmin local query-monthly-users-registered-by-group
            month    |            name            | count
         ------------+----------------------------+-------
          2020-08-01 | Australian_government      |     1
          2020-08-01 | Australian_researchers_mix |     1
          2020-08-01 | RMIT_users                 |     1
          2020-08-01 | UQ_users                   |     3
          2020-07-01 | Australian_government      |     1
          2020-07-01 | Australian_researchers_mix |     6
          2020-07-01 | JCU_users                  |     2
          2020-07-01 | Monash_users               |     6
          2020-07-01 | QUT_users                  |     2
          2020-07-01 | RMIT_users                 |     1
          ...
EOF

if (( $# > 0 )); then
		where=" date_trunc('year', galaxy_user.create_time AT TIME ZONE 'UTC') = '$1-01-01'::date and"
fi

	read -r -d '' QUERY <<-EOF
		SELECT
			date_trunc('month', galaxy_user.create_time)::DATE AS month,
            galaxy_group.name,
            count(*)
		FROM
			galaxy_user,
            user_group_association,
            galaxy_group
		WHERE
			$where
        	galaxy_user.id = user_group_association.user_id and
        	galaxy_group.id = user_group_association.group_id
		GROUP BY
			month,
            galaxy_group.name
		ORDER BY
			month DESC
EOF
}

local_query-monthly-jobs-by-group(){ ## [year]: Number of jobs run each month per group
    handle_help "$@" <<-EOFhelp
		Number of jobs run per group per month. (Optional: for a given year.)

		$ gxadmin local query-monthly-jobs-by-group
		    month    |            name            | count
		 ------------+----------------------------+-------
		  2020-08-01 | AdelaideU_users            |    52
		  2020-08-01 | Australian_government      |   512
		  2020-08-01 | Australian_researchers_mix |   909
		  2020-08-01 | CSIRO                      |    76
		  2020-08-01 | History Retention Keeplist |    18
		  2020-08-01 | JCU_users                  |     3
		  2020-08-01 | Monash_users               |   255
		  2020-08-01 | QUT_users                  |     6
		  2020-08-01 | UNSW_users                 |    45
		  2020-08-01 | UoM_users                  |   353
		  2020-08-01 | UoSydney_users             |   369
		  ...

EOFhelp

	if (( $# > 0 )); then
        where=" date_trunc('year', job.create_time AT TIME ZONE 'UTC') = '$1-01-01'::date and"
	fi

	read -r -d '' QUERY <<-EOF
		SELECT
			date_trunc('month', job.create_time)::DATE AS month,
			galaxy_group.name,
			count(*)
		FROM
			job,
			galaxy_group,
			user_group_association
		WHERE
			$where
        	job.user_id = user_group_association.user_id and
        	galaxy_group.id = user_group_association.group_id
		GROUP BY
			month,
			galaxy_group.name
		ORDER BY
			month DESC
EOF
}

local_query-monthly-new-data-by-group(){ ## [year] [--human]: Amount of new data created each month per group
	handle_help "$@" <<-EOFhelp
		Amount of new data created each month per group (Optional: for a given year)

		$ gxadmin local query-monthly-new-data-by-group --human
		   month    |            name            | pg_size_pretty
		------------+----------------------------+----------------
		 2020-08-01 | AdelaideU_users            | 31 MB
		 2020-08-01 | Australian_government      | 76 GB
		 2020-08-01 | Australian_researchers_mix | 886 GB
		 2020-08-01 | CSIRO                      | 518 MB
		 2020-08-01 | History Retention Keeplist | 341 MB
		 2020-08-01 | JCU_users                  | 303 bytes
		 2020-08-01 | Monash_users               | 150 GB
		 2020-08-01 | QUT_users                  | 1715 MB
		 2020-08-01 | UNSW_users                 | 100 GB
		 2020-08-01 | UoM_users                  | 683 GB
		 2020-08-01 | UoSydney_users             | 34 GB
		 ...

EOFhelp

#size="round(sum(coalesce(dataset.total_size, dataset.file_size, 0))*9.3132257e-10) AS size"
size="sum(coalesce(dataset.total_size, dataset.file_size, 0)) AS size"
if (( $# > 0 )); then
	for args in "$@"; do
		if [ "$args" = "--human" ]; then
			size="pg_size_pretty(sum(coalesce(dataset.total_size, dataset.file_size, 0))) AS size"
		else
			where=" date_trunc('year', dataset.create_time AT TIME ZONE 'UTC') = '$args-01-01'::date and"
		fi
	done
fi

	read -r -d '' QUERY <<-EOF
		SELECT
			date_trunc('month', dataset.create_time AT TIME ZONE 'UTC')::date AS month,
			galaxy_group.name,
			$size
		FROM
			dataset,
			galaxy_group,
			history_dataset_association,
			history,
			user_group_association
		WHERE
			$where
			dataset.id = history_dataset_association.dataset_id and
			history_dataset_association.history_id = history.id and
			history.user_id = user_group_association.user_id and
			user_group_association.group_id = galaxy_group.id
		GROUP BY
			month,
			galaxy_group.name
		ORDER BY
			month DESC
EOF
}

local_query-monthly-users-active-by-group(){ ## [year]: Number of unique users who ran a job per group each month
	handle_help "$@" <<-EOFhelp
		Number of unique users who ran a job per group each month (Optional: for a given year)

		$ gxadmin local query-monthly-users-active-by-group
		   month    |            name            | active_users
		------------+----------------------------+--------------
		 2020-08-01 | AdelaideU_users            |            3
		 2020-08-01 | Australian_government      |            8
		 2020-08-01 | Australian_researchers_mix |           14
		 2020-08-01 | CSIRO                      |            1
		 2020-08-01 | History Retention Keeplist |            2
		 2020-08-01 | JCU_users                  |            1
		 2020-08-01 | Monash_users               |           14
		 2020-08-01 | QUT_users                  |            5
		 2020-08-01 | RMIT_users                 |            2
		 2020-08-01 | UNSW_users                 |            4
		 2020-08-01 | UoM_users                  |            3
		 2020-08-01 | UoSydney_users             |            4
		 2020-08-01 | UQ_users                   |           33
		 2020-08-01 | USQ_users                  |            2
		 2020-08-01 | UTas_users                 |           12
		 2020-08-01 | UWA_users                  |            2
		 2020-07-01 | AdelaideU_users            |            4
		 2020-07-01 | Australian_government      |            8
		 2020-07-01 | Australian_researchers_mix |           31
		 2020-07-01 | CSIRO                      |            2
		 2020-07-01 | Curtin_users               |            1
		 2020-07-01 | GriffithU_users            |            2
		 2020-07-01 | History Retention Keeplist |            4
		 2020-07-01 | JCU_users                  |            3
		 2020-07-01 | Monash_users               |           18
		 2020-07-01 | QUT_users                  |            3
EOFhelp

	if(( $# > 0 )); then
		where=" date_trunc('year', job.create_time AT TIME ZONE 'UTC') = '$1-01-01'::date and "
	fi

	read -r -d '' QUERY <<-EOF
		SELECT
			date_trunc('month', job.create_time AT TIME ZONE 'UTC')::date as month,
			galaxy_group.name,
			count(distinct job.user_id) as active_users
		FROM
			job,
			user_group_association,
			galaxy_group
		WHERE
			$where
			job.user_id = user_group_association.user_id and
			user_group_association.group_id = galaxy_group.id
		GROUP BY
			month,
			galaxy_group.name
		ORDER BY
			month DESC
EOF
}

local_query-monthly-jobs-per-destination(){ ## [year]: Number of jobs per month sent to each destination
	handle_help "$@" <<-EOFhelp
	Number of jobs sent to each destination per month (Optional: for a given year)

	$ gxadmin local query-monthly-jobs-per-destination
	   month    |     destination_id      | count
	------------+-------------------------+-------
	 2020-08-01 | pulsar-mel3_big         |   131
	 2020-08-01 | pulsar-mel3_big_canu    |    40
	 2020-08-01 | pulsar-mel3_big_trinity |    43
	 2020-08-01 | pulsar-mel3_mid         |   535
	 2020-08-01 | pulsar-mel3_small       |    99
	 2020-08-01 | pulsar-mel_big          |    32
	 2020-08-01 | pulsar-mel_mid          |  2534
	 2020-08-01 | pulsar-mel_small        |  2099
	 2020-08-01 | pulsar-paw_big          |   223
	 2020-08-01 | pulsar-paw_mid          |   597
	 2020-08-01 | slurm_16slots           |   139
	 2020-08-01 | slurm_1slot             | 10463
	 2020-08-01 | slurm_1slot_upload      |  4913
	 2020-08-01 | slurm_2slots            |   757
	 2020-08-01 | slurm_32slots           |     1
	 2020-08-01 | slurm_3slots            |  1693
	 2020-08-01 | slurm_5slots            |  2114
	 2020-08-01 | slurm_7slots            |   590
	 2020-08-01 | slurm_9slots            |   357
	 2020-08-01 |                         |   856
	 2020-07-01 | pulsar-mel3_big         |   468
	 2020-07-01 | pulsar-mel3_big_canu    |    53
	 2020-07-01 | pulsar-mel3_big_trinity |    90
	 2020-07-01 | pulsar-mel3_mid         |  9698
	 2020-07-01 | pulsar-mel3_small       |   328
	 2020-07-01 | pulsar-mel_big          |    57
EOFhelp

	if(( $# > 0 )); then
 		where="WHERE date_trunc('year', job.create_time AT TIME ZONE 'UTC') = '$1-01-01'::date"
 	fi

	read -r -d '' QUERY <<-EOF
		SELECT
			date_trunc('month', job.create_time AT TIME ZONE 'UTC')::DATE AS month,
			job.destination_id,
			count(*)
		FROM
			job
		$where
		GROUP BY
			month,
			job.destination_id
		ORDER BY
			month DESC
EOF
}

local_query-histogram-of-history-update-time(){
	handle_help "$@" <<-EOFhelp
	Produces data for a histogram of history update times by weeks

	$ gxadmin local query-histogram-of-history-update-time

     count |    week
    -------+------------
       408 | 2019-11-04
       453 | 2019-11-11
       361 | 2019-11-18
       233 | 2019-11-25
       385 | 2019-12-02
       187 | 2019-12-09
       149 | 2019-12-16
        57 | 2019-12-23
        50 | 2019-12-30
       109 | 2020-01-06
       122 | 2020-01-13
       191 | 2020-01-20
       176 | 2020-01-27
       252 | 2020-02-03
       235 | 2020-02-10
       347 | 2020-02-17
      9341 | 2020-02-24
       405 | 2020-03-02
       253 | 2020-03-09
       618 | 2020-03-16
       419 | 2020-03-23
       526 | 2020-03-30
       509 | 2020-04-06
       199 | 2020-04-13
EOFhelp

	read -r -d '' QUERY <<-EOF
		SELECT
            date_trunc('week', update_time AT TIME ZONE 'UTC')::date as week,
			count(*)
		FROM
			history
		WHERE
            deleted = 'false'
		GROUP BY
			week
		ORDER BY
			week
EOF
}

local_query-histogram-of-history-create-time() { ## : Produces data for a histogram of history create times by weeks
	handle_help "$@" <<-EOFhelp
	Produces data for a histogram of history create times by weeks

	$ gxadmin local query-histogram-of-history-create-time

     count |    week
    -------+------------
       408 | 2019-11-04
       453 | 2019-11-11
       361 | 2019-11-18
       233 | 2019-11-25
       385 | 2019-12-02
       187 | 2019-12-09
       149 | 2019-12-16
        57 | 2019-12-23
        50 | 2019-12-30
       109 | 2020-01-06
       122 | 2020-01-13
       191 | 2020-01-20
       176 | 2020-01-27
       252 | 2020-02-03
       235 | 2020-02-10
       347 | 2020-02-17
      9341 | 2020-02-24
       405 | 2020-03-02
       253 | 2020-03-09
       618 | 2020-03-16
       419 | 2020-03-23
       526 | 2020-03-30
       509 | 2020-04-06
       199 | 2020-04-13
EOFhelp

	read -r -d '' QUERY <<-EOF
		SELECT
            date_trunc('week', create_time AT TIME ZONE 'UTC')::date as week,
			count(*)
		FROM
			history
		WHERE
            deleted = 'false'
		GROUP BY
			week
		ORDER BY
			week
EOF
}

local_query-histogram-of-history-create-update-time() { ## : Produces data for a histogram of history create and update times by weeks
	handle_help "$@" <<-EOFhelp
	Produces data for a histogram of history create and update times by weeks

	$ gxadmin local query-histogram-of-history-create-update-time

EOFhelp

	read -r -d '' QUERY <<-EOF
		SELECT
            date_trunc('week', create_time AT TIME ZONE 'UTC')::date as week,
			count(create_time),
            count(update_time)
		FROM
			history
		WHERE
            deleted = 'false'
		GROUP BY
			week
		ORDER BY
			week
EOF
}

local_query-job-input-datasets() { ##? [job_id] : Show job input datasets with sizes for a job
	# similar to gxadmin query-job-inputs but with sizes
	arg_id="$1"
	handle_help "$@" <<-EOF
	Shows a table of job input datasets with file_size and total size for a given job id
	
	$ gxadmin local query-job-input-datasets 4092986755

	 hda_id  |            hda_name             |  d_id   | d_state | d_file_size | d_total_size
	---------+---------------------------------+---------+---------+-------------+--------------
	91237625 | SRR7692603:forward uncompressed | 3545195 | ok      | 4810 MB     | 4810 MB
	91237627 | SRR7692603:reverse uncompressed | 3545196 | ok      | 4845 MB     | 4845 MB

	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				hda.id AS hda_id,
				hda.name AS hda_name,
				d.id AS d_id,
				d.state AS d_state,
				pg_size_pretty(d.file_size) AS d_file_size,
				pg_size_pretty(d.total_size) AS d_total_size
			FROM job j
				JOIN job_to_input_dataset jtid
					ON j.id = jtid.job_id
				JOIN history_dataset_association hda
					ON hda.id = jtid.dataset_id
				JOIN dataset d
					ON hda.dataset_id = d.id
			WHERE j.id = $arg_id
	EOF
}


local_query-job-input-size() { ##? [job_id]: Shows details of a job including the sum of input dataset sizes
	job_id="$1"
	handle_help "$@" <<-EOF

	Shows details of a job including the sum of input dataset sizes for a given job ID

	$ gxadmin local query-job-input-size 4212421

	 job_id  |          created           |          updated           | username | state |                       tool_id                        | sum_input_size | destination  | external_id
	---------+----------------------------+----------------------------+----------+-------+------------------------------------------------------+----------------+--------------+-------------
	 4212421 | 2021-03-01 23:14:05.770694 | 2021-03-01 23:14:12.965732 | koala    | error | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 1615 kB        | slurm_3slots | 444

	EOF
	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.create_time as created,
				j.update_time as updated,
				u.username,
				j.state as state,
				j.tool_id as tool_id,
				(
					SELECT
					pg_size_pretty(SUM(d.total_size))
					FROM dataset d, history_dataset_association hda, job_to_input_dataset jtid
					WHERE hda.dataset_id = d.id
					AND jtid.job_id = j.id
					AND hda.id = jtid.dataset_id
				) as sum_input_size,
				j.destination_id as destination,
				j.job_runner_external_id as external_id
			FROM job j, galaxy_user u
			WHERE j.user_id = u.id
			AND j.id = $job_id
	EOF
}

local_query-job-input-size-by-tool() { ##? [tool] <limit> : Show most recent jobs for a tool including total input size
	tool_substr="$1"
	[ ! "$2" ] && limit="10" || limit="$2"
	handle_help "$@" <<-EOF

	Produces a table of n most recently created jobs for a tool.  The first argument is a substring of the tool ID.
	The second optional argument is the number of rows to display (default 10).
	**NOTE**: since the tool argument is a substring of the ID, to specifically look for bwa jobs without including
	bwa_mem jobs the appropriate argument would be '/bwa/bwa/'

	$ gxadmin local query-job-input-size-by-tool multiqc

	 job_id  |          created           |          updated           |   username   | state |                       tool_id                        | sum_input_size | destination  | external_id
	---------+----------------------------+----------------------------+--------------+-------+------------------------------------------------------+----------------+--------------+-------------
	 4212521 | 2021-03-01 23:40:43.571578 | 2021-03-01 23:40:57.23172  | platypus     | ok    | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 27 kB          | slurm_3slots | 492
	 4212432 | 2021-03-01 23:19:33.729478 | 2021-03-01 23:19:46.422826 | emu          | ok    | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 18 kB          | slurm_3slots | 460
	 4212427 | 2021-03-01 23:15:36.339832 | 2021-03-01 23:15:46.32736  | koala        | ok    | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 18 kB          | slurm_3slots | 446
	 4212426 | 2021-03-01 23:15:20.785234 | 2021-03-01 23:15:32.484563 | wombat       | ok    | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 27 kB          | slurm_3slots | 445
	 4212421 | 2021-03-01 23:14:05.770694 | 2021-03-01 23:14:12.965732 | koala        | error | toolshed.g2.bx.psu.edu/repos/iuc/multiqc/multiqc/1.9 | 1615 kB        | slurm_3slots | 444

	EOF


	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.create_time as created,
				j.update_time as updated,
				u.username,
				j.state as state,
				j.tool_id as tool_id,
				(
					SELECT
					pg_size_pretty(SUM(d.total_size))
					FROM dataset d, history_dataset_association hda, job_to_input_dataset jtid
					WHERE hda.dataset_id = d.id
					AND jtid.job_id = j.id
					AND hda.id = jtid.dataset_id
				) as sum_input_size,
				j.destination_id as destination,
				j.job_runner_external_id as external_id
			FROM job j, galaxy_user u
			WHERE j.user_id = u.id
			AND position('$tool_substr' in j.tool_id)>0
			ORDER BY j.create_time desc
			LIMIT $limit
	EOF
}

local_query-all-jobs() {  ##? <limit> : List most recently updated jobs
	[ ! "$1" ] && limit="50" || limit="$1"
	handle_help "$@" <<-EOF

	Produces a table of all jobs by creation time.  This is much like `gxadmin query queue-detail`
	but it returns jobs in all states. By default it returns 50 jobs.  It can return more
	or less if a limit is supplied.

	$ gxadmin local query-all-jobs 4
	 job_id  |          created           |     username     | state  |                                 tool_id                                  |    destination
	---------+----------------------------+------------------+--------+--------------------------------------------------------------------------+--------------------
	 2209960 | 2021-03-23 11:33:59.382595 | frederick_smythe | queued | upload1                                                                  | slurm_1slot_upload
	 2209959 | 2021-03-23 11:33:42.422161 | frederick_smythe | error  | toolshed.g2.bx.psu.edu/repos/iuc/newick_utils/newick_display/1.6+galaxy1 | pulsar-mel3_small
	 2209958 | 2021-03-23 11:33:17.148529 | frederick_smythe | ok     | upload1                                                                  | slurm_1slot_upload
	 2209957 | 2021-03-23 11:28:40.726797 | frederick_smythe | error  | toolshed.g2.bx.psu.edu/repos/iuc/newick_utils/newick_display/1.6+galaxy1 | pulsar-mel3_small

	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.create_time as created,
				u.username,
				j.state as state,
				j.tool_id as tool_id,
				j.destination_id as destination
			FROM job j, galaxy_user u
			WHERE j.user_id = u.id
			ORDER BY j.update_time desc
			LIMIT $limit
	EOF
}

local_query-walltime-size-by-tool() { ##? [tool substr] <limit> : Show most recent jobs with walltime and total input size for a given tool
	tool_substr="$1"
	[ ! "$2" ] && limit="50" || limit="$2"
	handle_help "$@" <<-EOF

	Produces a table with input size and running times for a given tool, provided as the first argument.
	The argument is a substring of the tool_id e.g. trinity, trinity/2.9.1+galaxy1, Count1.  The second
	argument is the number of rows to return (optional, default: 50).

	$ gxadmin local query-walltime-size-by-tool busco 5
	 job_id  |          created           |          updated           |   username    |  state  |                          tool_id                           | runtime  | sum_input_size | destination
	---------+----------------------------+----------------------------+---------------+---------+------------------------------------------------------------+----------+----------------+--------------
	 7535204 | 2021-09-14 06:13:44.820678 | 2021-09-14 07:27:47.494749 | julia         | ok      | toolshed.g2.bx.psu.edu/repos/iuc/busco/busco/5.0.0+galaxy0 | 01:13:59 | 148 MB         | slurm_3slots
	 7533738 | 2021-09-13 14:10:02.462621 | 2021-09-13 18:06:15.366452 | paul          | ok      | toolshed.g2.bx.psu.edu/repos/iuc/busco/busco/5.2.2+galaxy0 | 03:56:10 | 31 MB          | slurm_1slot
	 7533781 | 2021-09-13 14:53:51.879839 | 2021-09-13 14:54:24.656188 | kevin         | ok      | toolshed.g2.bx.psu.edu/repos/iuc/busco/busco/5.2.2+galaxy0 | 00:00:31 | 2244 kB        | slurm_1slot
	 7533323 | 2021-09-13 08:15:12.673086 | 2021-09-13 12:10:33.847549 | paul          | ok      | toolshed.g2.bx.psu.edu/repos/iuc/busco/busco/5.2.2+galaxy0 | 03:55:18 | 31 MB          | slurm_1slot
	 7533213 | 2021-09-13 05:59:59.559287 | 2021-09-13 07:21:51.458181 | paul          | deleted | toolshed.g2.bx.psu.edu/repos/iuc/busco/busco/5.2.2+galaxy0 |          | 3970 MB        | slurm_3slots

	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.create_time as created,
				j.update_time as updated,
				u.username,
				j.state as state,
				j.tool_id as tool_id,
				(SELECT 
					TO_CHAR((jmn.metric_value || ' second')::interval, 'HH24:MI:SS')
					FROM job_metric_numeric jmn
					WHERE jmn.metric_name = 'runtime_seconds'
					AND jmn.job_id = j.id
				) as runtime,
				(
					SELECT
					pg_size_pretty(SUM(d.total_size))
					FROM dataset d, history_dataset_association hda, job_to_input_dataset jtid
					WHERE hda.dataset_id = d.id
					AND jtid.job_id = j.id
					AND hda.id = jtid.dataset_id
				) as sum_input_size,
				j.destination_id as destination
			FROM job j
			FULL OUTER JOIN galaxy_user u ON j.user_id = u.id
			WHERE j.user_id = u.id
			AND position('$tool_substr' in j.tool_id)>0
			ORDER BY j.update_time desc
			LIMIT $limit
	EOF
}

local_query-jobs-running-at-datetime() { ##? <datetime> : See completed jobs created before and completed after a given datetime
	datetime="$1"
	handle_help "$@" <<-EOF

	Find all jobs in queued, running or ok state that were created before and updated after a given datetime.  This was written with the aim of finding
	non-deleted jobs that may have two sets of data files due to the hierarchical object store path having changed while they were queued or running.

	$ gxadmin local query-jobs-running-at-datetime "2021-09-28 14:00"
	 job_id  |          created           |          updated           | user_id | state |                                   tool_id                                   | destination_id
	---------+----------------------------+----------------------------+---------+-------+-----------------------------------------------------------------------------+-----------------
	 7396484 | 2021-09-28 13:59:25.91883  | 2021-09-28 15:09:09.148783 |   24601 | ok    | toolshed.g2.bx.psu.edu/repos/devteam/tophat2/tophat2/2.1.1                  | pulsar-mel3_mid
	 7396483 | 2021-09-28 13:58:59.578761 | 2021-09-28 15:06:50.605129 |   24601 | ok    | toolshed.g2.bx.psu.edu/repos/devteam/tophat2/tophat2/2.1.1                  | slurm_1slot
	 7396455 | 2021-09-28 13:27:11.979348 | 2021-09-28 14:01:13.616717 |    2468 | ok    | toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.73+galaxy0             | pulsar-mel3_mid
	 7396432 | 2021-09-28 12:59:47.650807 | 2021-09-28 14:49:57.488824 |    2468 | ok    | toolshed.g2.bx.psu.edu/repos/pjbriggs/trimmomatic/trimmomatic/0.36.6        | slurm_3slots
	 7396349 | 2021-09-28 12:35:23.974676 | 2021-09-28 14:32:15.411004 |   21583 | ok    | toolshed.g2.bx.psu.edu/repos/iuc/unicycler/unicycler/0.4.8.0                | pulsar-mel3_mid

	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.create_time as created,
				j.update_time as updated,
				j.user_id as user_id,
				j.state as state,
				j.tool_id as tool_id,
				j.destination_id as destination_id
			FROM job j
			WHERE j.create_time < '$datetime'
			AND j.update_time > '$datetime'
			AND j.state in ('queued', 'running', 'ok', 'error')
			ORDER BY j.create_time desc
	EOF
}

local_query-queue() { ##? [--all] [--seconds] [--since-update]: Detailed overview of running and queued jobs with cores/mem info
	# this is a copy of gxadmin query queue-detail with job destination info (cores/mem/partition) added and runner_id, count removed
	handle_help "$@" <<-EOF
			$ gxadmin local query-queue
			  state  |  id  | extid |                          tool_id                          | username | time_since_creation |       handler       | cores | mem  | partition | destination_id
			---------+------+-------+-----------------------------------------------------------+----------+---------------------+---------------------+-------+------+-----------+-----------------
			 running | 4385 | 4011  | upload1                                                   | cat      | 00:01:01.518932     | main.job-handlers.2 | 2     | 6144 |           | slurm
			 queued  | 4387 | 4012  | toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.2 | cat      | 00:00:24.377336     | main.job-handlers.2 | 1     | 3072 |           | slurm
			 queued  | 4388 | 4388  | toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.2 | cat      | 00:00:13.254505     | main.job-handlers.1 | 1     | 3072 |           | pulsar-nci-test
			 queued  | 4389 | 4013  | toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.2 | cat      | 00:00:01.834048     | main.job-handlers.2 | 1     | 3072 |           | slurm
	EOF

	fields="count=9"
	tags="state=0;id=1;extid=2;tool_id=3;username=4;handler=6;job_runner_name=7;destination_id=8"

	d=""
	nonpretty="("
	time_column="job.create_time"
	time_column_name="time_since_creation"

	if [[ -n "$arg_all" ]]; then
		d=", 'new'"
	fi
	if [[ -n "$arg_seconds" ]]; then
		fields="$fields;time_since_creation=5"
		nonpretty="EXTRACT(EPOCH FROM "
	fi
	if [[ -n "$arg_since_update" ]]; then
		time_column="job.update_time"
		time_column_name="time_since_update"
	fi

	username=$(gdpr_safe galaxy_user.username username "Anonymous User")

	read -r -d '' QUERY <<-EOF
		SELECT
			job.state,
			job.id,
			job.job_runner_external_id as extid,
			job.tool_id,
			$username,
			$nonpretty now() AT TIME ZONE 'UTC' - $time_column) as $time_column_name,
			job.handler,
			(REGEXP_MATCHES(encode(job.destination_params, 'escape'), 'ntasks=(\d+)'))[1] as cores,
			(REGEXP_MATCHES(encode(job.destination_params, 'escape'), 'mem=(\d+)'))[1] as mem,
			(REGEXP_MATCHES(encode(job.destination_params, 'escape'), 'partition=(\d+)'))[1] as partition,
			COALESCE(job.destination_id, 'none') as destination_id
		FROM job
		FULL OUTER JOIN galaxy_user ON job.user_id = galaxy_user.id
		WHERE
			state in ('running', 'queued'$d)
		ORDER BY
			state desc,
			$time_column_name desc
	EOF
}

local_query-galaxy-session-user(){ ## [username]: Query user session information
    handle_help "$@" <<-EOF
        Find session information about the given user, specified by username

        $ gxadmin local query-galaxy-session-user username
EOF

    if (( $# > 0 )); then
        read -r -d '' QUERY <<-EOF
            SELECT *
            FROM galaxy_session
            LEFT JOIN galaxy_user AS galaxy_session_user
            ON galaxy_session.user_id = galaxy_session_user.id
            WHERE galaxy_session_user.username = '$1';
EOF
    fi
}

local_query-oom-jobs() { ##? <limit> : Show most recent jobs with 'Killed' in tool_stderr or 'terminated because it used more memory' in info
	[ ! "$1" ] && limit="50" || limit="$1"
	handle_help "$@" <<-EOF

	Produces a table of jobs that have failed due to out of memory errors.
	Optional argument of number of rows to return (default: 50).

	$ gxadmin local query-oom-jobs 3
	   id    | username |        create_time         |                             tool_id                             | cores | mem_mb |   input_size   |    destination_id
	---------+----------+----------------------------+-----------------------------------------------------------------+-------+--------+----------------+----------------------
	 6994190 | anthony  | 2023-08-30 22:26:38.904458 | toolshed.g2.bx.psu.edu/repos/iuc/minimap2/minimap2/2.20+galaxy2 | 16    | 62874  | 8947 MB        | pulsar-QLD
	 6993519 | bob      | 2023-08-30 16:16:13.27616  | toolshed.g2.bx.psu.edu/repos/chemteam/bio3d_pca/bio3d_pca/2.3.4 | 1     | 65536  | 5667 MB        | pulsar-qld-high-mem1
	 6993500 | julia    | 2023-08-30 16:01:10.09834  | toolshed.g2.bx.psu.edu/repos/iuc/abyss/abyss-pe/2.3.6+galaxy0   | 16    | 62874  | 22 MB          | pulsar-mel3
	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				u.username,
				j.update_time as updated,
				j.tool_id as tool_id,
				(REGEXP_MATCHES(encode(j.destination_params, 'escape'), 'ntasks=(\d+)'))[1] as cores,
				(REGEXP_MATCHES(encode(j.destination_params, 'escape'), 'mem=(\d+)'))[1] as mem,
				(
					SELECT pg_size_pretty(SUM(total_size))
					FROM (
						SELECT DISTINCT hda.id as hda_id, d.total_size as total_size
						FROM dataset d, history_dataset_association hda, job_to_input_dataset jtid
						WHERE hda.dataset_id = d.id
						AND jtid.job_id = j.id
						AND hda.id = jtid.dataset_id
					) as foo
				) as input_size,
				j.destination_id as destination
			FROM job j
			FULL OUTER JOIN galaxy_user u ON j.user_id = u.id
			WHERE j.user_id = u.id
			AND (
				position('This job was terminated because it used more memory' in j.info)>0
				OR position('Killed' in j.tool_stderr)>0
			)
			ORDER BY j.update_time desc
			LIMIT $limit
	EOF
}

local_query-tool-memory() { ##? <limit>
	tool_substr="$1"
	[ ! "$2" ] && limit="50" || limit="$2"
	handle_help "$@" <<-EOF

	For a substring of a tool ID, list the most recent completed jobs with annotated with
		tpv_cores, tpv_mem_mb (the cores and memory allocated to the job)
		input_size (the sum of the input file sizes)
		job_max_mem (from the cgroup job metric value memory.max_usage_in_bytes)
		runtime (from the job metric runtime_seconds)
	The is an optional second argument of number of rows to return (default 50)

	$gxadmin local query-tool-memory flye 3
	 job_id  |          updated           | state |                            tool_id                             | tpv_cores | tpv_mem_mb | input_size | job_max_mem | runtime  |     destination
	---------+----------------------------+-------+----------------------------------------------------------------+-----------+------------+------------+-------------+----------+----------------------
	 6999140 | 2023-09-05 10:19:45.517908 | ok    | toolshed.g2.bx.psu.edu/repos/bgruening/flye/flye/2.9.1+galaxy0 | 120       | 1968128    | 34 GB      | 728 GB      | 42:01:32 | pulsar-qld-high-mem1
	 7020524 | 2023-09-05 08:32:40.891413 | ok    | toolshed.g2.bx.psu.edu/repos/bgruening/flye/flye/2.9.1+galaxy0 | 16        | 62874      | 420 MB     | 9186 MB     | 00:11:28 | pulsar-mel3
	 7020514 | 2023-09-05 08:19:25.951317 | ok    | toolshed.g2.bx.psu.edu/repos/bgruening/flye/flye/2.9.1+galaxy0 | 8         | 31437      | 207 MB     | 8991 MB     | 00:03:40 | pulsar-mel3

	EOF

	read -r -d '' QUERY <<-EOF
			SELECT
				j.id as job_id,
				j.update_time as updated,
				j.state as state,
				j.tool_id as tool_id,
				(REGEXP_MATCHES(encode(j.destination_params, 'escape'), 'ntasks=(\d+)'))[1] as tpv_cores,
				(REGEXP_MATCHES(encode(j.destination_params, 'escape'), 'mem=(\d+)'))[1] as tpv_mem_mb,
				(
					SELECT pg_size_pretty(SUM(total_size))
					FROM (
						SELECT DISTINCT hda.id as hda_id, d.total_size as total_size
						FROM dataset d, history_dataset_association hda, job_to_input_dataset jtid
						WHERE hda.dataset_id = d.id
						AND jtid.job_id = j.id
						AND hda.id = jtid.dataset_id
					) as foo
				) as input_size,
				(SELECT 
					pg_size_pretty(jmn.metric_value)
					FROM job_metric_numeric jmn
					WHERE jmn.metric_name = 'memory.max_usage_in_bytes'
					AND jmn.job_id = j.id
				) as job_max_mem,
				(SELECT 
					TO_CHAR((jmn.metric_value || ' second')::interval, 'HH24:MI:SS')
					FROM job_metric_numeric jmn
					WHERE jmn.metric_name = 'runtime_seconds'
					AND jmn.job_id = j.id
				) as runtime,
				j.destination_id as destination
			FROM job j
			WHERE position('$tool_substr' in j.tool_id)>0
			AND j.state in ('ok', 'error')
			ORDER BY j.update_time desc
			LIMIT $limit
	EOF
}