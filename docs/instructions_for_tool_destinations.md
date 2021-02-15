# Modifying Tool Destinations

We use the NML's tool_destinations.yml system included in Galaxy as the 'DTD' dynamic job destination.

### The `tool_destinations.yml` file

The tool destination file that gets copied to Galaxy Australia lives in the `files/galaxy/dynamic_job_rules/pawsey/dynamic_rules/tool_destinations.yml` file.

This file sets out rules for selection of destinations for various jobs based upon: Tool Id, User and Input file sizes.

Examples:

```yaml
tools:
    # A generic ruleset for a tool based on file size.. Smaller jobs will be sent to a small destination
    # and a large job will be sent to a larger location, default desinations are set for jobs outside the rules.
    spades:
        rules:
            - rule_type: file_size
              nice_value: 0
              lower_bound: 0 MB
              upper_bound: 15 MB
              destination: pulsar-mel_small
            - rule_type: file_size
              nice_value: 0
              lower_bound: 15 MB
              upper_bound: 1 GB
              destination: slurm_9slots
        default_destinaion: pulsar-mel3_big
    # Jobs can be sent to different destinations based on their run-time arguments. Default destination is
    # important incase arguments are specified outside those in the rules.
    kraken2:
        rules:
            - rule_type: arguments
              nice_value: 0
              destination: slurm_16slots
              arguments:
                  kraken2_database: "2020-02-04T223652Z_standard_kmer-len_35_minimizer-len_31_minimizer-spaces_6"
            - rule_type: arguments
              nice_value: 0
              destination: slurm_5slots
              arguments:
                  kraken2_database: "2020-02-05T235531Z_minikraken2_v2_8GB"
        default_destination: slurm_16slots
    # Rules can be assigned for an array of users as in the example below
    ncbi_blastn_wrapper:
        rules:
            - rule_type: file_size
              nice_value: 0
              destination: pulsar-mel3_mid
              lower_bound: 0
              upper_bound: 1 GB
              users:
                  - i.makunin@uq.edu.au
        default_destination: slurm_5slots
    
#The default destination for tools that aren't specified above
default_destination: slurm_1slot

verbose: True
```

### The available destinations

The destinations available for the jobs are listed in the job conf file. In the repo this is in yaml format in the `host_vars/pawsey_job_conf.yml` file. Only destinations listed in this file are valid. They will be checked upon pull request creation.

## Modifying `tool_destinations.yml` in Github GUI

The easiest way for team members to modify the `tool_destinations.yml` file is via the Github GUI. 

**Procedure**

1. Navigate to the repo at: [https://github.com/usegalaxy-au/infrastructure](https://github.com/usegalaxy-au/infrastructure)
2. Open the view of the `tool_destinations.yml` file (click on the file) in the `files/galaxy/dynamic_job_rules/pawsey/dynamic_rules` directory.
3. Click the "Pencil" (edit) icon at the top of the file view.
4. Edit the file.
5. In the *Commit Changes* box at the bottom of the screen, give a description of what changes you made and why.
6. Make sure you select "Create a **new branch** for this commit and start a pull request."
7. Click "Propose Changes"

This will create a Github Pull Request (PR) with your changes in it ready for review by a committer.

Upon making a change and opening a PR, a validator will run to check that the contents of the file is valid and all destinations exist.

