import os
import yaml
import csv
import datetime

from galaxy.util.tool_shed.xml_util import parse_xml
from galaxy.util import xml_to_string

from pytz import timezone

"""
Add labels to shed_tool_conf.xml. There are labels are from tool_labels.yml file such as
'training-only'.  Labels are also added based on installation dates from the log generated
in the usegalaxy-au-tools tool installation process.
"""

date_format = '%d/%m/%y %H:%M:%S'
aest = timezone('Australia/Queensland')

log_file = 'automated_tool_installation_log.tsv'
tool_labels_file = 'tool_labels.yml'
hidden_tools_file = 'hidden_tools.yml'
shed_tool_conf_file = 'shed_tool_conf.xml'
new_label = 'new'
updated_label = 'updated'
display_new_days = 14
display_updated_days = 14

def main():
    for required_file in ['automated_tool_installation_log.tsv', 'tool_labels.yml', 'shed_tool_conf.xml']:
        if not os.path.exists(required_file):
            raise Exception(f'Required file {required_file} is missing')

    def filter_new(row):
        return row['Status'] == 'Installed' and in_time_window(row['Date (AEST)'], display_new_days) and row['New Tool'] == 'True'

    def filter_updated(row):
        return row['Status'] == 'Installed' and in_time_window(row['Date (AEST)'], display_updated_days) and row['New Tool'] == 'False'

    def load_log(filter=None):
        """
        Load the installation log tsv file and return it as a list row objects, i.e.
        [{'Build Num.': '156', 'Name': 'abricate', ...}, {'Build Num.': '156', 'Name': 'bedtools', ...},...]
        The filter argument is a function that takes a row as input and returns True or False
        """
        table = []
        with open(log_file) as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            for row in reader:
                if not filter or filter(row):
                    table.append(row)
        return table

    with open(tool_labels_file) as handle:
        tool_labels_constant = yaml.safe_load(handle)

    if os.path.exists(hidden_tools_file):
        with open(hidden_tools_file) as handle:
            hidden_tool_ids = yaml.safe_load(handle).get('hidden_tool_ids', [])
    else:
        hidden_tool_ids = []
    
    tool_labels_dynamic = {
        new_label: load_log(filter=filter_new),
        updated_label: load_log(filter=filter_updated),
    }

    tree, error_message = parse_xml(shed_tool_conf_file)
    root = tree.getroot()
    # shed_tool_conf.xml has multiple section elements containing tools
    # loop through all sections and tools
    for section in root:
        if section.tag == 'section':
            for tool in list(section):
                if tool.tag == 'tool':
                    tool_id = tool.find('id').text
                    name = tool.find('repository_name').text
                    owner = tool.find('repository_owner').text
                    revision = tool.find('installed_changeset_revision').text
                    # remove all existing labels
                    tool.attrib.pop('labels', None)
                     # replace labels from dict
                    labels_for_tool = []
                    for label in tool_labels_constant:
                        for id in tool_labels_constant[label]:
                            if tool_id == id or (
                                id.endswith('*') and get_deversioned_id(id) == get_deversioned_id(tool_id)
                            ):
                                labels_for_tool.append(label)
                                break
                    for label in tool_labels_dynamic:
                        for row in tool_labels_dynamic[label]:
                            if row['Name'] == name and row['Owner'] == owner and row['Installed Revision'] == revision:
                                labels_for_tool.append(label)
                                break
                    tool.attrib.pop('hidden', None)
                    for id in hidden_tool_ids:
                        if tool_id == id or (
                            id.endswith('*') and get_deversioned_id(id) == get_deversioned_id(tool_id)
                        ):
                            tool.set('hidden', 'True')
                            break
                    if labels_for_tool:
                        tool.set('labels', ','.join(labels_for_tool))


    with open(shed_tool_conf_file, 'w') as handle:
        handle.write(xml_to_string(root, pretty=True))


def get_deversioned_id(tool_id):
    return '/'.join(tool_id.split('/')[:-1])


def in_time_window(time_str, days):
    # return True if time_str is less than a certain number of days ago
    parsed_datetime = datetime.datetime.strptime(time_str, date_format)
    converted_datetime = aest.localize(parsed_datetime)
    return converted_datetime > datetime.datetime.now(tz=aest) - datetime.timedelta(days=days)

if __name__ == "__main__":
    main()
