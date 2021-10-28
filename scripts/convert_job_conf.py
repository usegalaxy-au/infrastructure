import argparse
import oyaml as yaml

"""
Convert values from galaxy_jobconf into a yaml job configuration file.  This needs input yaml files
that contain galaxy_jobconf (previously used for templating job_conf.xml) and galaxy_handler_count
"""

# credit to stackoverflow user's solutions for yaml representation of quoted and blank values
# https://stackoverflow.com/questions/67476386/python-yaml-script-and-double-quotes
# https://stackoverflow.com/questions/30134110/how-can-i-output-blank-value-in-python-yaml-file/37445121
class DoubleQuoted(str):
  pass

def represent_double_quoted(dumper, data):
  return dumper.represent_scalar(yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG,
      data, style='"')

yaml.add_representer(DoubleQuoted, represent_double_quoted)
yaml.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
)

def flatten(dict_item):
    item = dict_item.copy()
    item_id = item['id']
    if item.get('params'):
        for param in item['params']:
            item[param] = item['params'][param]
        del item['params']
    del item['id']
    return item_id, quote_values(item)

def quote_values(dict_item):
    for key in dict_item:
        if isinstance(dict_item[key], str) and (' ' in dict_item[key] or '{{' in dict_item[key]):
            dict_item[key] = DoubleQuoted(dict_item[key])
    return dict_item

def main():
    parser = argparse.ArgumentParser(description='Uninstall tool from a galaxy instance')
    parser.add_argument('input', nargs='+', help='Input file/files with galaxy_jobconf and galaxy_handler_count')
    parser.add_argument('-o', '--output', help='Output yaml file')
    args = parser.parse_args()
    input = args.input
    output = args.output
    if not args.output:
        output = 'job_conf_converted.yml'

    config_yaml = {}
    for input in args.input:
        with open(input) as handle:
            config_yaml.update(yaml.safe_load(handle))

    input_jc = config_yaml['galaxy_jobconf']
    galaxy_handler_count = config_yaml['galaxy_handler_count']

    runners = {}
    environments = {}
    handling = {}
    tools = []
    limits = []
    default_destination = input_jc['default_destination']

    if galaxy_handler_count:
        handling['processes'] = [{f'main.job-handler.{n+1}': None} for n in range(int(galaxy_handler_count))]
    for h in input_jc.get('handlers'):
        if h != 'count':
            handling[h] = input_jc['handlers'][h]

    for p in input_jc['plugins']:
        runner_id, runner = flatten(p)
        runners[runner_id] = runner

    for d in input_jc['destinations']:
        environment_id, environment = flatten(d)
        environments[environment_id] = environment

    for t in input_jc['tools']:
        tools.append(quote_values({
            'id': t['id'],
            'environment': t['destination'],
        }))
    
    for l in input_jc['limits']:
        limit = l.copy()
        if limit.get('destination_user_concurrent_jobs'):
            limit['environment_user_concurrent_jobs'] = limit['destination_user_concurrent_jobs']
            del limit['destination_user_concurrent_jobs']
        if limit.get('destination_user_concurrent_jobs'):
            limit['environment_total_concurrent_jobs'] = limit['destination_total_concurrent_jobs']
            del limit['destination_total_concurrent_jobs']
        limits.append(quote_values(limit))

    job_conf = {
        'handling': handling,
        'runners': runners,
        'execution': {
            'default': default_destination,
            'environments': environments,
        },
        'tools': tools,
        'limits': limits
    }

    with open(output, 'w') as handle:
        yaml.dump(job_conf, handle, width=1000)

if __name__ == "__main__":
    main()
