import argparse
import sys
import time
import datetime as dt

from bioblend import ConnectionError
from bioblend.galaxy import GalaxyInstance as bioblend_GalaxyInstance
from bioblend.galaxy.client import Client

install_timeout = 600
sleep_interval = 10

"""
Install unresolved conda environments on a Galaxy instance.  This can be run at any time but its purpose
is to set up environments for galaxy built-in tools on a new instance.  By default resolve only builtin
environments but set --all to include environments for toolshed tools
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
    [resolver_info] = galaxy_instance.tool_dependencies.summarize_toolbox(index_by='tool', tool_ids=[tool_id])
    return 'NullDependency' not in [s['model_class'] for s in resolver_info['status']]


def user_is_admin(galaxy_instance):
    return galaxy_instance.config.get_config().get('is_admin_user', False)


class ToolDependenciesClient(Client):  # TODO: try getting this into bioblend

    def __init__(self, galaxy_instance):
        self.module = 'dependency_resolvers'
        super().__init__(galaxy_instance)

    def summarize_toolbox(self, index=None, tool_ids=[], resolver_type=None, include_containers=None, container_type=None, index_by=None):
        """
        GET /api/dependency_resolvers/toolbox

        Summarize requirements across toolbox (for Tool Management grid). This is an experiemental
        API particularly tied to the GUI - expect breaking changes until this notice is removed.

        :type   index:    int
        :param  index:    index of the dependency resolver
        :type   tool_ids: list
        :param  tool_ids: tool_ids to return when index_by=tool
        :type   resolver_type:  str
        :param  resolver_type:  restrict to specified resolver type
        :type   include_containers: bool
        :param  include_containers: include container resolvers in resolution
        :type   container_type: str
        :param  container_type: restrict to specified container type
        :type   index_by: str
        :param  index_by: By default consider only context of requirements, group tools by requirements.
                          Set this to 'tools' to summarize across all tools though. Tools may provide additional
                          context for container resolution for instance.

        :rtype:     list
        :returns:   dictified descriptions of the dependencies, with attribute
            `dependency_type: None` if no match was found.
            For example::
        
            [{'requirements': [{'name': 'galaxy_sequence_utils',
                                'specs': [],
                                'type': 'package',
                                'version': '1.1.4'},
                               {'name': 'bx-python',
                                'specs': [],
                                'type': 'package',
                                'version': '0.8.6'}],
              'status': [{'cacheable': False,
                          'dependency_type': None,
                          'exact': True,
                          'model_class': 'NullDependency',
                          'name': 'galaxy_sequence_utils',
                          'version': '1.1.4'},
                          {'cacheable': False,
                          'dependency_type': None,
                          'exact': True,
                          'model_class': 'NullDependency',
                          'name': 'bx-python',
                          'version': '0.8.6'}],
              'tool_ids': ['vcf_to_maf_customtrack1']}]        
        """

        params = {}
        if index:
            params['index'] = str(index)
        if tool_ids:
            params['tool_ids'] = ','.join(tool_ids)
        if resolver_type:
            params['resolver_type'] = resolver_type
        if include_containers is not None:
            params['include_containers'] = str(include_containers)
        if container_type:
            params['container_type'] = container_type
        if index_by:
            params['index_by'] = index_by

        url = self._make_url() + '/toolbox'
        return self._get(url=url, params=params)


class GalaxyInstance(bioblend_GalaxyInstance):

    def __init__(self, url, key=None, **kwargs):
        super().__init__(url, key, **kwargs)
        self.tool_dependencies = ToolDependenciesClient(self)


if __name__ == '__main__':
    main()
