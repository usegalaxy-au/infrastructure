![galaxy_australia_logo.png](images/Galaxy_australia_white.png)

# Galaxy Australia's Infrastructure Playbooks

This repository contains the terraform and ansible necessary to create and maintain the Galaxy Australia ecosystem. The contents of this repository are very specific to Galaxy Australia and are not general in any way. 

Galaxy Australia can be accessed at: [**https://usegalaxy.org.au**](https://usegalaxy.org.au)

If you wish to use Ansible and Terraform for your own Galaxy server then head over to the [Galaxy Project's Git Hub](https://github.com/galaxyproject/) for more resources or checkout the amazing range of [Galaxy Administration with Ansible tutorials](https://training.galaxyproject.org/training-material/topics/admin/) located at the [Galaxy Training Network's site](https://training.galaxyproject.org).

Galaxy Australia currently runs a number of instances and nodes, mostly on cloud resources using Openstack. The head node of Galaxy Australia runs on [AARNet](https://www.aarnet.edu.au/) virtual machines in Sydney, with additional infrastructure deployed at the University of Queensland, the University of Melbourne and NCI.

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

These playbooks are designed for [Ansible](https://www.ansible.com) versions 2.9 and above, but we recommend running with ansible-core version `2.12`. This can be installed with pip. Note that PYPI versions are different to the ansible-core version:

```py
# Requires python >=3.8; <3.12
pip install ansible==5.6.0  # this gets you ansible-core==2.12
```

Further installation instructions for Ansible can be found [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

#### Ansible Roles Required

Most of the roles used here are from [Ansible Galaxy](https://galaxy.ansible.com/)

They are all listed in the `requirements.yml` file. They can be installed locally with the `ansible-galaxy` command.

```bash
ansible-galaxy install -p roles -r requirements.yml
```
#### Running the playbooks

Each playbook can be run with:

```bash
ansible-playbook -i hosts --vault-password-file <vault-password-file> --private-key <ssh_key> <playbook>
```
where you supply the `<vault-password-file>`, the `<ssh_key>` and the playbook you want to run.

## Contributions

All contributions to these playbooks are to be made by pull request. 

We strongly suggest you fork the repository.

Jobs are scheduled using the [Total Perspective Vortex](https://github.com/galaxyproject/total-perspective-vortex) (TPV) job scheduler. See also: [TPV by example](docs/topics/tpv_by_example.rst).

## Maintenance

This repository is maintained by the Galaxy Australia team.

**Credits:**

[Contributors](https://github.com/usegalaxy-au/infrastructure/graphs/contributors)


### TIaaS Documentation

The documentation/instructions for the Galaxy Australia implementation of Galaxy Europe's TIaaS (Training Infrastructure as a Service) system can be found [here](docs/TIaaS.md)


| [![melbourne_bioinformatics_logo.png](images/melbourne_bio.png)](https://melbournebioinformatics.org.au) | [![QFAB_logo_2020.png](images/QFAB_logo_2020.png)](https://www.qcif.edu.au/services/bioinformatics/) |
|-|-|
