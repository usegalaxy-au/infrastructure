import oyaml as yaml
import os
import re
from bioblend.galaxy import GalaxyInstance

# TODO: handle user and argument based rules

path_to_vortex_rules = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../files/galaxy/dynamic_job_rules/pawsey/total_perspective_vortex'
)

local_tools_not_in_panel = ['upload1', 'Extract genomic DNA 1']  # galaxy built-in tools that are not returned by the get_tools() function
oddly_named_data_managers = ['kraken2_build_database']  # data manager tool short ids that do not contain the substring 'data_manager'

galaxy_instance = GalaxyInstance('https://usegalaxy.org.au')
galaxy_tool_ids = [t['id'] for t in galaxy_instance.tools.get_tools()]

tool_destinations_file = '/Users/cat/dev/infrastructure/files/galaxy/dynamic_job_rules/pawsey/dynamic_rules/tool_destinations.yml'
job_config_file = '/Users/cat/dev/infrastructure/templates/galaxy/config/pawsey_job_conf.yml.j2'


def file_size_to_GB_string(file_size):  # not a full conversion: 500 MB -> (500/1024)  # almost like opposite of pg_pretty
    if file_size in (0, '0'):
        return '0'
    if file_size == 'Infinity':
        return 'Infinity'
    size, unit = file_size.split()
    if unit == 'GB':
        return size
    elif unit == 'MB':
        return f'({size}/1024)'
    elif unit == 'KB':
        return f'({size}/(1024*1024))'
    elif unit == 'B':
        return f'({size}/(1024*1024*1024))'
    else:
        raise Exception('File size thing is not working')

def make_lower_upper_expression(lower, upper):
    if lower == '0':
        return f'input_size < {upper}'
    elif upper == 'Infinity':
        return f'input_size >= {lower}'
    else:
        return f'input_size >= {lower} and input_size < {upper}'

def get_native_spec(env):
    return env.get('nativeSpecification') or env.get('submit_native_specification')

def get_cores_from_env(env):
    print(env)
    ntasks_pattern = re.compile('.*--ntasks=(?P<ntasks>\d+).*')
    native_spec = get_native_spec(env)
    ntasks = int(re.match(ntasks_pattern, native_spec).groupdict().get('ntasks'))
    return ntasks

def get_mem_from_env(env):
    mem_pattern = re.compile('.*--mem=(?P<mem>\d+).*')
    native_spec = get_native_spec(env)
    mem = int(re.match(mem_pattern, native_spec).groupdict().get('mem'))
    return mem

with open(job_config_file) as handle:
    job_conf = yaml.safe_load(handle)
    envs = job_conf.get('execution').get('environments')

with open(tool_destinations_file) as handle:
    tool_dests = yaml.safe_load(handle)['tools']

vortex_tools = {}
for tool_id in tool_dests:
    tool = tool_dests[tool_id]
    pulsar_allowed = False
    file_size_rules = []
    user_rules = []  # skip these for now
    allowed_dests = [tool['default_destination']]
    for rule in tool.get('rules', []):
        if rule['rule_type'] == 'file_size' and not rule.get('users'):
            new_rule = {
                'lower': file_size_to_GB_string(rule['lower_bound']),
                'upper': file_size_to_GB_string(rule['upper_bound']),
            }
            if rule['destination'] == 'fail':
                new_rule.update({'fail': rule['fail_message']})
            else:
                new_rule['cores'] = get_cores_from_env(envs[rule['destination']])           
                new_rule['mem'] = get_mem_from_env(envs[rule['destination']])
            file_size_rules.append(new_rule)
            allowed_dests.append(rule['destination'])
    if any([x.startswith('pulsar') for x in allowed_dests]):
        pulsar_allowed = True
    if not file_size_rules:
        file_size_rules.append({
            'lower': '0',
            'upper': 'Infinity',
            'cores': get_cores_from_env(envs[tool['default_destination']]),
            'mem': get_mem_from_env(envs[tool['default_destination']]),
        })
    # now order them from lowest to highest.  Assume they make sense.
    file_size_rules = sorted(file_size_rules, key = lambda x: 10**9 if x['upper'] == 'Infinity' else eval(x['upper']))
    if file_size_rules and not any([x['lower'] == '0' for x in file_size_rules]):
        lowest_rule = {
            'lower': '0',
            'upper': file_size_rules[0]['lower'],
            'cores': get_cores_from_env(envs[tool['default_destination']]),
            'mem': get_mem_from_env(envs[tool['default_destination']]),           
        }
        file_size_rules = [lowest_rule] + file_size_rules
    if file_size_rules and not any([x['upper'] == 'Infinity' for x in file_size_rules]):
        highest_rule = {
            'lower': file_size_rules[-1]['upper'],
            'upper': 'Infinity',
            'cores': get_cores_from_env(envs[tool['default_destination']]),
            'mem': get_mem_from_env(envs[tool['default_destination']]),            
        }
        file_size_rules.append(highest_rule)
    vortex_tool = {}
    if pulsar_allowed:
        vortex_tool['inherits'] = 'pulsar_preferred'  # or something
    # define the core setting as the lowest rule, add all file size rules as separate rules
    tool_rules = file_size_rules[1:]
    vortex_tool['cores'] = file_size_rules[0]['cores']
    if tool_rules:
        vortex_tool['rules'] = []
        for rule in tool_rules:
            the_rule = {'match': make_lower_upper_expression(lower=rule['lower'], upper=rule['upper'])}
            # for key in rule.keys():
            #     if key in ['cores', 'mem', 'fail']:
            #         the_rule[key] = rule[key]
            if 'cores' in rule.keys():
                the_rule.update({'cores': rule['cores']})
            if 'mem' in rule.keys():
                mem_gb = rule['mem'] / 1024
                the_rule.update({'mem': mem_gb})
            if 'fail' in rule.keys():
                the_rule.update({'fail': rule['fail']})               

            vortex_tool['rules'].append(the_rule)

    tool_id_regexes = []
    # tool might be a short id or a toolshed tool id
    # print(sorted(galaxy_tool_ids))
    matching_galaxy_toolshed_tool_id_regexes = list(set([
        f'{("/").join(id.split("/")[:-1])}/.*' for id in galaxy_tool_ids if '/' in id and id.split('/')[-2] == tool_id
    ]))
    matching_galaxy_local_tool_id_regexes = [id for id in galaxy_tool_ids if id == tool_id] # i.e. exact match regex
    included_unmatched_tools = [id for id in local_tools_not_in_panel if id == tool_id] # i.e. exact match regex
    data_managers = [f'.*{tool_id}.*'] if 'data_manager' in tool_id or tool_id in oddly_named_data_managers else []
    new_ids = matching_galaxy_toolshed_tool_id_regexes + matching_galaxy_local_tool_id_regexes + included_unmatched_tools + data_managers
    if len(new_ids) == 0:
        print(f'No galaxy tool found for short_id {tool_id}')
    if len(new_ids) > 1:
        print(f'{len(new_ids)} found matching short_id {tool_id}: {", ".join(new_ids)}')
    for new_id in new_ids:
        vortex_tools[new_id] = vortex_tool.copy()

with open(os.path.join(path_to_vortex_rules, 'vortex_tools_auto.yml'), 'w') as handle:
    yaml.dump({'tools': vortex_tools}, handle)

# split destinations by runners if the destinations have native specifications 
destinations = {}

new_dest_ids = []
for runner_id in job_conf['runners'].keys():
    runner_envs = [env_id for env_id in envs if envs[env_id]['runner'] == runner_id and get_native_spec(envs[env_id])]
    if len(runner_envs) == 0:
        continue
    if len(runner_envs) == 1:
        new_dest_id = runner_envs[0]
    else:
        e0, e1 = runner_envs[:2]
        longest_prefix_length = max([x for x in range(min(len(e0), len(e1))) if e0[:x] == e1[:x]])
        new_dest_id = e0[:longest_prefix_length].strip('_')
    # choose the highest cores/mem of all of the original destinations for native spec
    # e.g. for slurm, choose native specification from slurm_32slots
    sorted_env_ids = sorted(runner_envs, key=lambda x: get_cores_from_env(envs[x]), reverse=True)
    new_dest = envs[sorted_env_ids[0]].copy()
    destinations[new_dest_id] = new_dest

with open(os.path.join(path_to_vortex_rules, 'destinations_for_job_conf_auto.yml'), 'w') as handle:
    yaml.dump({'environments': destinations}, handle)

vortex_destinations = {}
for id in destinations:
    env = destinations[id]
    ntasks = get_cores_from_env(env)
    mem = get_mem_from_env(env)
    vortex_dest = {'cores': ntasks, 'mem': mem/1024, 'scheduling': {}}
    vortex_dest['scheduling']['accept'] = [id]  # each destination gets its own tag
    if id.startswith('pulsar'):
        vortex_dest['scheduling']['require'] = ['pulsar']
    vortex_destinations[id] = vortex_dest
    
with open(os.path.join(path_to_vortex_rules, 'vortex_destinations_auto.yml'), 'w') as handle:
    yaml.dump({'destinations': vortex_destinations}, handle)

#  f'{x:.2f}' format x to 2 decimal places
