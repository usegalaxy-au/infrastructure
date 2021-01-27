#!/usr/bin/env python

import os

# from galaxy.jobs import JobDestination
# from galaxy.jobs.mapper import JobMappingException

from galaxy.jobs.dynamic_tool_destination import map_tool_to_destination
from random import sample

TOOL_DESTINATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tool_destinations.yml')

pulsar_user_destinations = {  # test pulsar users whose shed-tool jobs will always run on pulsars
    'pulsar_mel2_user@usegalaxy.org.au': 'pulsar-mel_small',
    'pulsar_mel3_user@usegalaxy.org.au': 'pulsar-mel3_small',
    'pulsar_paw_user@usegalaxy.org.au': 'pulsar-paw_small',
}

def gateway(job, app, tool, user_email):
    """
    Function to specify the destination for a job.  At present this is exactly the same
    as using dynamic_dtd with tool_destinations.yml but can be extended to more complex
    mapping such as limiting resources based on user group or selecting destinations
    based on queue size.
    Arguments to this function can include app, job, job_id, job_wrapper, tool, tool_id,
    user, user_email (see https://docs.galaxyproject.org/en/latest/admin/jobs.html)
    """

    # map jobs from pulsar_user_destinations
    if user_email in pulsar_user_destinations.keys():
        if hasattr(tool, 'id') and isinstance(tool.id, str) and tool.id.startswith('toolshed'):  # map shed tools only
            return pulsar_user_destinations[user_email]

    destination = map_tool_to_destination(job, app, tool, user_email, path=TOOL_DESTINATION_PATH)
    return destination

