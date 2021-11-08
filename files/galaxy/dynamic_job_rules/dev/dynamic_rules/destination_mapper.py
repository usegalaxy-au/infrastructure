#!/usr/bin/env python

import os

# from galaxy.jobs import JobDestination
# from galaxy.jobs.mapper import JobMappingException

from galaxy.jobs.dynamic_tool_destination import map_tool_to_destination
# from random import sample

TOOL_DESTINATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tool_destinations.yml')

user_destinations = {
                        'pulsar_user@usegalaxy.org.au': 'pulsar_destination',
                        'eugpu@usegalaxy.org.au': 'pulsar-eu-gpu-test'
                    }

pulsar_list = ['fasta-stats', 'bwa_mem']


def gateway(job, app, tool, user, user_email):
    """
    Function to specify the destination for a job.  At present this is exactly the same
    as using dynamic_dtd with tool_destinations.yml but can be extended to more complex
    mapping such as limiting resources based on user group or selecting destinations
    based on queue size.
    Arguments to this function can include app, job, job_id, job_wrapper, tool, tool_id,
    user, user_email (see https://docs.galaxyproject.org/en/latest/admin/jobs.html)
    """

    if user_email in user_destinations.keys():
        if hasattr(tool, 'id') and isinstance(tool.id, str) and tool.id.startswith('toolshed'):  # map shed tools only
            return user_destinations[user_email]
    if user:
        user_roles = [role.name for role in user.all_roles() if not role.deleted]

        # If any of these are prefixed with 'training-'
        if any([role.startswith('training-') for role in user_roles]):
            # Then they are a training user, we will send their jobs to pulsar,
            # Or give them extra resources
            if hasattr(tool, 'id') and isinstance(tool.id, str) and tool.id.startswith('toolshed') and tool.id.split('/')[-2] in pulsar_list:
                return app.job_config.get_destination('pulsar_destination')
            else:
                return app.job_config.get_destination('slurm_2slots')

    destination = map_tool_to_destination(job, app, tool, user_email, path=TOOL_DESTINATION_PATH)
    return destination
