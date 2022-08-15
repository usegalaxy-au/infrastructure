#!/usr/bin/env python

import argparse
import pathlib
import re
import subprocess

"""
Script to set object_store_id of each dataset and metadata_file in the database.  When using a hierarchical
object store this field is not set.  When using a distributed object store each dataset needs to have an
object_store_id corresponding to the id of the backend in the object store, i.e:
    `<backend id="dev_objects_1" type="disk" weight="0" store_by="id">
        <files_dir path="/mnt/galaxy/data" />
    </backend>`
Usage: To set object_store_id to "dev_objects_1" for all items in /mnt/galaxy/data, run
$ python set_object_store_id.py --path /mnt/galaxy/data --id dev_objects_1
"""

def update_dataset_object_store_ids(temp_data, object_store_id, counter):
    dataset_ids = ','.join([y['id'] for y in temp_data])
    command = f'psql -c "update dataset set object_store_id = \'{object_store_id}\' where id in ({dataset_ids});"'
    # print(command)
    response_code = subprocess.call(command, shell = True)
    print(f'updated {counter} datasets, response code {response_code}')

def update_metadata_file_object_store_ids(temp_data, object_store_id, counter):
    metadata_ids = ','.join([y['id'] for y in temp_data])
    command = f'psql -c "update metadata_file set object_store_id = \'{object_store_id}\' where id in ({metadata_ids});"'
    # print(command)
    response_code = subprocess.call(command, shell = True)
    print(f'updated {counter} metadata files, response code {response_code}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='file path')
    parser.add_argument('-i', '--id', help='object store id')
    args = parser.parse_args()

    answer = input(f"Set all datasets in {args.path} to have object_store_id {args.id}: Type y/yes to and enter to continue: ")
    if not answer in ['y', 'yes']:
        raise Exception()

    counter = 0
    temp_data = []

    for i in pathlib.Path(args.path).glob('**/dataset_*.dat'):
        counter += 1
        test = re.search("dataset_(\d+).dat", str(i))
        if hasattr(test, 'group'):
            id = test.group(1)
        else:
            continue
        temp_data.append({'id': id, 'path': str(i)})
        if counter % 1000 == 0:
            update_dataset_object_store_ids(temp_data=temp_data, object_store_id=args.id, counter=counter)
            temp_data = []
    # update object store ids for whatever remains
    update_dataset_object_store_ids(temp_data=temp_data, object_store_id=args.id, counter=counter)

    counter = 0
    temp_data = []
    for i in pathlib.Path(args.path).glob('**/metadata_*.dat'):
        counter += 1
        test = re.search("metadata_(\d+).dat", str(i))
        if hasattr(test, 'group'):
            id = test.group(1)
        else:
            continue
        temp_data.append({'id': id, 'path': str(i)})
        if counter % 1000 == 0:
            update_metadata_file_object_store_ids(temp_data=temp_data, object_store_id=args.id, counter=counter)
            temp_data = []
    # update object store ids for whatever remains
    update_metadata_file_object_store_ids(temp_data=temp_data, object_store_id=args.id, counter=counter)

if __name__ == '__main__':
    main()
