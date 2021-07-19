import argparse
import sys
import time
import datetime as dt

from bioblend import ConnectionError
from bioblend.galaxy import GalaxyInstance

install_timeout = 600
sleep_interval = 10

"""
Install unresolved conda environments on a Galaxy instance.  This can be run at any time but its purpose
is to set up environments for galaxy built-in tools on a new instance.  By default resolve only builtin
environments but set --all to include environments for toolshed tools

requires bioblend>=0.16.0
"""

def main():
    parser = argparse.ArgumentParser(description='Install unresolved conda environments on a Galaxy instance')
    parser.add_argument('-g', '--galaxy_url', help='URL of Galaxy instance')
    parser.add_argument('-a', '--api_key', help='Galaxy admin api key')
    parser.add_argument('--all', action='store_true', help='Build all unresolved environments including those for shed tools')
    args = parser.parse_args()
    
    galaxy_instance = GalaxyInstance(args.galaxy_url, args.api_key)

    if not user_is_admin(galaxy_instance):
        print('Error: galaxy user must be an admin')
        return

    tool_groups = []
    toolbox = galaxy_instance.tool_dependencies.summarize_toolbox()
    for dependency_set in toolbox:
        if 'NullDependency' in [s['model_class'] for s in dependency_set['status']]:  # if true, the environment is not resolved
            builtin_tools_in_list = not all([x.startswith('toolshed') for x in dependency_set['tool_ids']])
            if args.all or builtin_tools_in_list:
                tool_groups.append(dependency_set['tool_ids'])

    print('%d environments to install\n' % len(tool_groups))
    for counter, tool_group in enumerate(tool_groups):
        prog = '%d/%d' % (counter + 1, len(tool_groups))
        tool_id = tool_group[0]  # install dependencies for one tool in the group as all tools in the group require the same environment
        try:
            galaxy_instance.tools.install_dependencies(tool_id)
            print('(%s) Resolved dependencies for %s' % (prog, ', '.join(tool_group)))
        except ConnectionError:  # api call will time out after 3 minutes or so
            # wait for resolution before moving on to the next tool
            resolved = False
            start = dt.datetime.now()
            while (dt.datetime.now() - start) < dt.timedelta(seconds=install_timeout) and not resolved:
                time.sleep(sleep_interval)
                resolved = dependency_is_resolved(galaxy_instance, tool_id)
            if resolved:
                print('(%s) Resolved dependencies for %s' % (prog, ', '.join(tool_group)))
            else:
                print('(%s) Timed out without resolving dependencies for %s' % (prog, ', '.join(tool_group)))


def dependency_is_resolved(galaxy_instance, tool_id):
    [resolver_info] = galaxy_instance.tool_dependencies.summarize_toolbox(index_by='tools', tool_ids=[tool_id])
    return 'NullDependency' not in [s['model_class'] for s in resolver_info['status']]


def user_is_admin(galaxy_instance):
    return galaxy_instance.config.get_config().get('is_admin_user', False)


if __name__ == '__main__':
    main()
