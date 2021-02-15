# Modifying Tool Destinations

We use the NML's tool_destinations.yml system included in Galaxy as the 'DTD' dynamic job destination.

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