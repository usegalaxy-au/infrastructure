import oyaml as yaml
import re
from bioblend.galaxy import GalaxyInstance


# todo: the gffread rule will not translate well

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

ntasks_pattern = re.compile('.*--ntasks=(?P<ntasks>\d+).*')

galaxy_instance = GalaxyInstance('https://usegalaxy.org.au')

tool_destinations_file = '/Users/cat/dev/infrastructure/files/galaxy/dynamic_job_rules/pawsey/dynamic_rules/tool_destinations.yml'

job_config_file = '/Users/cat/dev/infrastructure/templates/galaxy/config/pawsey_job_conf.yml.j2'

destination_cores = {}

with open(job_config_file) as handle:
    envs = yaml.safe_load(handle).get('execution').get('environments')

for env_id in envs:
    env = envs[env_id]
    native_spec = env.get('nativeSpecification') or env.get('submit_native_specification')
    if native_spec:
        ntasks = int(re.match(ntasks_pattern, native_spec).groupdict().get('ntasks'))
        destination_cores[env_id] = ntasks

destination_cores['fail'] = 'fail'

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
        if rule['rule_type'] == 'file_size':
            new_rule = {
                'lower': file_size_to_GB_string(rule['lower_bound']),
                'upper': file_size_to_GB_string(rule['upper_bound']),
            }
            if rule['destination'] == 'fail':
                new_rule.update({'fail': rule['fail_message']})
            else:
                new_rule['cores'] = destination_cores[rule['destination']]            
            file_size_rules.append(new_rule)
        allowed_dests.append(rule['destination'])
    if any([x.startswith('pulsar') for x in allowed_dests]):  # careful: there are some blast rules that go pulsar or slurm depending on params
        pulsar_allowed = True
    if not file_size_rules:
        file_size_rules.append({
            'lower': '0',
            'upper': 'Infinity',
            'cores': destination_cores[tool['default_destination']]
        })
    # now order them from lowest to highest.  Assume they make sense.
    file_size_rules = sorted(file_size_rules, key = lambda x: 10**9 if x['upper'] == 'Infinity' else eval(x['upper']))
    if file_size_rules and not any([x['lower'] == '0' for x in file_size_rules]):
        lowest_rule = {
            'lower': '0',
            'upper': file_size_rules[0]['lower'],
            'cores': destination_cores[tool['default_destination']]            
        }
        file_size_rules = [lowest_rule] + file_size_rules
    if file_size_rules and not any([x['upper'] == 'Infinity' for x in file_size_rules]):
        highest_rule = {
            'lower': file_size_rules[-1]['upper'],
            'upper': 'Infinity',
            'cores': destination_cores[tool['default_destination']]            
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
            for key in rule.keys():
                if key in ['cores', 'fail']:
                    the_rule[key] = rule[key]
            vortex_tool['rules'].append(the_rule)
    vortex_tools[tool_id] = vortex_tool  # worry about proper tool regex next

with open('vortex_tools.yml', 'w') as handle:
    yaml.dump({'tools': vortex_tools}, handle)

    
