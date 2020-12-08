#!/usr/bin/env

#Imports

import subprocess
from collections import defaultdict
import re
import os
import string
import sys
import argparse
import datetime

def transform_groups(blob):
    lines = blob.stdout.decode('utf-8').split('\n')
    stat = defaultdict(lambda: defaultdict())
    months = []
    for line in lines:
        line = line.strip()
        if re.match(r'\d+', line):
            tmp = re.split("\s+\|\s+", line)
            if tmp[1] == 'History Retention Keeplist':
                continue
            stat[tmp[1]][tmp[0]] = tmp[2]
            months.append(tmp[0])
    months = set(months)

    output = 'User_group'
    for month in sorted(months):
        output += '\t' + str(month)
    output += '\n'

    for key in sorted(stat.keys()):
        output += key
        for month in sorted(months):
            if month in stat[key].keys():
                output += '\t' + str(stat[key][month])
            else:
                output += '\t0'
        output += '\n'
    return output

def transform_monthly(blob):
    lines = blob.stdout.decode('utf-8').split('\n')
    stat = defaultdict()
    for line in lines:
        line = line.strip()
        if re.match(r'\d+', line):
            tmp = re.split('\s+\|\s+', line)
            stat[tmp[0]] = tmp[1]
    output1 = ''
    output2 = ''
    for month in sorted(stat.keys()):
        output1 += '\t' + month
        output2 += '\t' + stat[month]
    output = output1 + '\n' + output2 + '\n'
    return output

def transform_destination(blob):
    lines = blob.stdout.decode('utf-8').split('\n')
    stat = defaultdict(lambda: defaultdict())
    months = []
    for line in lines:
        line = line.strip()
        if re.match(r'\d+', line):
            tmp = re.split("\|", line)
            tmp = list(map(str.strip, tmp))
            if tmp[1] == '':
                dest = 'Meta'
            else:
                dest = (tmp[1].split("_"))[0]
            if tmp[0] in stat[dest].keys():
                stat[dest][tmp[0]] += int(tmp[2])
            else:
                stat[dest][tmp[0]] = int(tmp[2])
            months.append(tmp[0])
    months = set(months)

    output = 'Destination'
    for month in sorted(months):
        output += '\t' + str(month)
    output += '\n'

    for key in sorted(stat.keys()):
        output += key
        for month in sorted(months):
            if month in stat[key].keys():
                output += '\t' + str(stat[key][month])
            else:
                output += '\t0'
        output += '\n'
    return output

def collect(queries, args):
    #get the year
    year = datetime.datetime.now().year
    for q in queries:
        #make command
        cmd = q['command'].split()
        if not args.initialize:
            cmd.append(str(year))
        db_stat = subprocess.run(cmd, stdout=subprocess.PIPE)
        if q['type'] == 'group':
            stat = transform_groups(db_stat)
        elif q['type'] == 'monthly':
            stat = transform_monthly(db_stat)
        elif q['type'] == 'destination':
            stat = transform_destination(db_stat)
        print(q['header'])
        print(stat)
        print()


#Main
def main():

    VERSION = 0.1
    AUTHOR = 'Simon Gladman'
    LICENSE = 'GPLv3'
    DATE_CREATED = 'Aug 2020'

    parser = argparse.ArgumentParser(description="Collects monthly statistics for Galaxy Australia")
    parser.add_argument("-i", "--initialize", help="Runs the script as though its the first time. Collects all stats from entire history.", action='store_true')
    #parser.add_argument("-c", "--config_file", help="The config file to use - contains all of the querys to run.")
    parser.add_argument("-t", "--type", help="Only run the queries of this type")
    parser.add_argument("-p", "--print_queries", help="Print out the queries to be collected and exit", action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    if args.version:
        print("monthly_stats_collector.py version: %.1f" % VERSION)
        return

    query_list = [
        {
            'header': 'Monthly Users Registered Per Group',
            'command': 'gxadmin local query-monthly-users-registered-by-group',
            'type': 'group'
        },
        {
            'header': 'Monthly Active Users Per Group',
            'command': 'gxadmin local query-monthly-users-active-by-group',
            'type': 'group'
        },
        {
            'header': 'Monthly Jobs Per Group',
            'command': 'gxadmin local query-monthly-jobs-by-group',
            'type': 'group'
        },
        {
            'header': 'Monthly New Data Per Group',
            'command': 'gxadmin local query-monthly-new-data-by-group',
            'type': 'group'
        },
        {
            'header': 'Monthly Jobs',
            'command': 'gxadmin query monthly-jobs',
            'type': 'monthly'
        },
        {
            'header': 'Monthly New Users',
            'command': 'gxadmin query monthly-users-registered',
            'type': 'monthly'
        },
        {
            'header': 'Monthly Users Active',
            'command': 'gxadmin query monthly-users-active',
            'type': 'monthly'
        },
        {
            'header': 'Monthly New Data',
            'command': 'gxadmin query monthly-data',
            'type': 'monthly'
        },
        {
            'header': 'Monthly Jobs Per Destination',
            'command': 'gxadmin local query-monthly-jobs-per-destination',
            'type': 'destination'
        }
    ]

    if args.print_queries:
        print('Query Type\tQuery Name\tQuery Command')
        for q in query_list:
            print(q['type'] + '\t' + q['header'] + '\t' + q['command'])
        exit()

    if args.type:
        queries = []
        for q in query_list:
            if q['type'] == args.type:
                queries.append(q)
        collect(queries, args)
    else:
        collect(query_list, args)


if __name__ == "__main__": main()
