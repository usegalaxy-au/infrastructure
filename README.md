![galaxy_australia_logo.png](images/Galaxy_australia_white.png)

# Galaxy Australia's Infrastructure Playbooks

This repository contains the terraform and ansible necessary to create and maintain the Galaxy Australia ecosystem. The contents of this repository are very specific to Galaxy Australia and are not general in any way. 

Galaxy Australia can be accessed at: [**https://usegalaxy.org.au**](https://usegalaxy.org.au)

If you wish to use Ansible and Terraform for your own Galaxy server then head over to the [Galaxy Project's Git Hub](https://github.com/galaxyproject/) for more resources or checkout the amazing range of [Galaxy Administration with Ansible tutorials](https://training.galaxyproject.org/training-material/topics/admin/) located at the [Galaxy Training Network's site](https://training.galaxyproject.org).

Galaxy Australia currently runs a number of instances and nodes, mostly on cloud resources using Openstack. They currently are: 

* **Galaxy Australia** - the main server
    * Located at the Pawsey Supercomputing Centre
    * Playbooks predicated with "pawsey-"
* **Galaxy Australia Staging** - the tool testing server
    * Located at the University of Melbourne
    * Playbooks predicated with "staging-"
* **Galaxy Australia Dev** - the development server
    * Located at the University of Melbourne
    * Playbooks predicated with "dev-"
* **Pulsar Mel** - Pulsar cluster dedicated to training jobs
    * Located at the University of Melbourne
* **Pulsar Mel3** - Pulsar cluster dedicated to long running and large jobs
    * Located at the University of Melbourne
* **Pulsar Paw** - Pulsar cluster dedicated to COVID-19 analysis
    * Located at the Pawsey Supercomputing Centre
* **Pulsar NCI** - Pulsar cluster used for various jobs ranging from training to general capacity
    * Located at NCI in Canberra  (National Computational Infrastructure)

## Operation/Running the Playbooks

### Terraform

[![terraform_logo.png](images/terraform_logo.png)](https://terraform.io)

We use [Terraform](https://terraform.io) to instantiate all of our VMs. Instructions for the installation of Terraform can be found [here](https://learn.hashicorp.com/tutorials/terraform/install-cli).

The terraform files contained here are for each of the clusters in the Galaxy Australia ecosystem. They also require the appropriate Openstack credentials file to be sourced before running.

To run the terraform scripts, go to the appropriate subfolder and test with:

```bash
terraform plan
```

This will show you what changes will be made. Once satisfied use:

```bash
terraform apply
```

### Ansible

[![ansible_logo.png](images/ansible_logo.png)](https://www.ansible.com/)

These playbooks are designed for [Ansible](https://www.ansible.com) versions 2.9 and above.

Installation instructions for Ansible can be found [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

#### Ansible Roles Required

Most of the roles used here are from [Ansible Galaxy](https://galaxy.ansible.com/)

They are all listed in the `requirements.yml` file. They can be installed locally with the `ansible-galaxy` command.

```bash
ansible-galaxy install -p roles -r requirements.yml
```

There are a few custom roles associated with these playbooks. They are:

| Role name | Purpose |
|-----------|---------|
| common    | Performs common tasks on our virtual machines including setting up users, installing some required packages amongst other tasks |
| mariadb | Sets up MariaDB for Slurm accounting on various clusters |
| mounts | Sets up NFS mounts for various clusters |
| pg-post-tasks | Adds some users and extra permissions to the Galaxy Database |
| slg.db-backup | Role to setup database backups for Galaxy Australia |
| slg.galaxy_stats | Sets up collection of statistics from Galaxy for Grafana |

#### Running the playbooks

Each playbook can be run with:

```bash
ansible-playbook -i hosts --vault-password-file <vault-password-file> --private-key <ssh_key> <playbook>
```
where you supply the `<vault-password-file>`, the `<ssh_key>` and the playbook you want to run.

## Contributions

All contributions to these playbooks are to be made by pull request. 

We strongly suggest you fork the repository.

Detailed instructions on modifying the tool destinations for jobs is located [here](docs/instructions_for_tool_destinations.md)

## Maintenance

This repository is maintained by the Galaxy Australia team.

**Credits:**

[Contributors](https://github.com/usegalaxy-au/infrastructure/graphs/contributors)



| [![melbourne_bioinformatics_logo.png](images/melbourne_bio.png)](https://melbournebioinformatics.org.au) | [![QFAB_logo_2020.png](images/QFAB_logo_2020.png)](https://www.qcif.edu.au/services/bioinformatics/) |
|-|-|


