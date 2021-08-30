#!/usr/bin/env python

import os

# from galaxy.jobs import JobDestination
# from galaxy.jobs.mapper import JobMappingException

from galaxy.jobs.dynamic_tool_destination import map_tool_to_destination
from random import sample

TOOL_DESTINATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tool_destinations.yml')

user_destinations = {  # test users whose shed-tool jobs should run at specific destinations
    'pulsar_mel2_user@usegalaxy.org.au': 'pulsar-mel_small',
    # 'pulsar_mel3_user@usegalaxy.org.au': 'pulsar-mel3_small',
    'pulsar_paw_user@usegalaxy.org.au': 'pulsar-paw_small',
    'phm1@genome.edu.au': 'pulsar-high-mem1_big',
    'phm2@genome.edu.au': 'pulsar-high-mem2_big',
    'jenkins_bot@usegalaxy.org.au': 'slurm_1slot',
    'testbot@usegalaxy.org': 'slurm_1slot',
}

pulsar_list = [
    'shovill', 'spades', 'velvet', 'velvetoptimiser', 'prokka', 'lastz_wrapper_2', 'raxml', 'fastqc',
    'abricate', 'snippy', 'bwa', 'bwa_mem', 'hisat2', 'htseq_count',
    'unicycler',
]
# pulsar_training_large = ['unicycler']


def gateway(job, app, tool, user, user_email):
    """
    Function to specify the destination for a job.  At present this is exactly the same
    as using dynamic_dtd with tool_destinations.yml but can be extended to more complex
    mapping such as limiting resources based on user group or selecting destinations
    based on queue size.
    Arguments to this function can include app, job, job_id, job_wrapper, tool, tool_id,
    user, user_email (see https://docs.galaxyproject.org/en/latest/admin/jobs.html)
    """

    # map jobs from user_destinations
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
                return app.job_config.get_destination('pulsar-mel_small')
            # elif hasattr(tool, 'id') and isinstance(tool.id, str) and tool.id.startswith('toolshed') and tool.id.split('/')[-2] in pulsar_training_large:
            #     return app.job_config.get_destination('pulsar-mel3_mid')
            else:
                return app.job_config.get_destination('slurm_training')

    destination = map_tool_to_destination(job, app, tool, user_email, path=TOOL_DESTINATION_PATH)
    return destination
