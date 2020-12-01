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

local_query-histogram-of-history-create-time(){
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

local_query-histogram-of-history-create-update-time(){
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

