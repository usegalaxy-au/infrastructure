######################################################################################
# Terraform for instantiation of Pulsar-NCI-Training
# Layout is:
#       * head node with large volume attached
#       * Multiple workers connected
# Local Variables contain most of the mutables for cluster. e.g. image, flavour sizes,
# worker numbers, key pair etc.
#
# Be careful editing especially in the worker loops. Best to only edit the local vars.
#
# 2021-09-14: Simon - Initial system
######################################################################################

######################################################################################
# Variables
######################################################################################

locals {
  worker_count      = 12
  tmp_disk_size     = 200
  avail_zone        = "CloudV3"
  key_pair          = "gvl_2019"
  image_id          = "7120863d-b414-4d16-a13a-c0866f917af4" #Ubuntu Focal Cloud Image 2021-09-08
  worker_flavour    = "c3pl.16c48m60d"

  #Loops for worker nodes - do not modify
  instances = toset(formatlist("%d", range(local.worker_count)))
  volumes = toset(flatten([ for instance in local.instances : "pulsar-nci-training-w${instance}-volume" ]))
  attachments = toset(flatten([ for instance in local.instances : {
      instance = instance
      volume = "pulsar-nci-training-w${instance}-volume"
    }]))
}

######################################################################################
# Instances
######################################################################################

# application server / web server
resource "openstack_compute_instance_v2" "pulsar-nci-training" {
  name            = "pulsar-nci-training"
  image_id        = local.image_id
  flavor_name     = "c3.8c16m10d"
  key_pair        = local.key_pair
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
}

#Worker nodes
resource "openstack_compute_instance_v2" "worker-nodes" {
  for_each          = local.instances
  name              = "pulsar-nci-training-w${each.value}"
  image_id          = local.image_id
  flavor_name       = local.worker_flavour
  key_pair          = local.key_pair
  security_groups   = ["ssh", "default"]
  availability_zone = local.avail_zone
  network {
    name = "aa63"
  }
}

######################################################################################
# Volumes
######################################################################################


# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "pulsar-nci-training-volume" {
  availability_zone = "CloudV3"
  name        = "pulsar-nci-training-volume"
  description = "Pulsar NCI Training Head Node Volume"
  size        = 10000
}

#Volumes for worker nodes
resource "openstack_blockstorage_volume_v2" "worker_tmp_disk" {
  for_each = local.volumes
  availability_zone = local.avail_zone
  name        = each.value
  description = "Worker temp disk"
  size        = local.tmp_disk_size
}

######################################################################################
# Attachments
######################################################################################

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pulsar-nci-training-volume-to-pulsar-nci-training" {
  instance_id = openstack_compute_instance_v2.pulsar-nci-training.id
  volume_id   = openstack_blockstorage_volume_v2.pulsar-nci-training-volume.id
}

# Attachment between worker nodes and worker temp volumes
resource "openstack_compute_volume_attach_v2" "attach-worker-volume-to-worker" {
  for_each = { for idx in local.attachments: idx.instance => idx }
  instance_id = openstack_compute_instance_v2.worker-nodes[each.value.instance].id
  volume_id   = openstack_blockstorage_volume_v2.worker_tmp_disk[each.value.volume].id
}

######################################################################################
# Networking
######################################################################################

#floating ips for project
resource "openstack_networking_floatingip_v2" "floatip_head" {
  pool = "external"
}

#Associate FIPs with instances
resource "openstack_compute_floatingip_associate_v2" "fip_head" {
  floating_ip = openstack_networking_floatingip_v2.floatip_head.address
  instance_id = openstack_compute_instance_v2.pulsar-nci-training.id
}

######################################################################################
# Outputs
######################################################################################

output "head_ip"{
  value = openstack_compute_instance_v2.pulsar-nci-training.access_ip_v4
}

output "head_volume_attachment_device" {
  value = openstack_compute_volume_attach_v2.attach-pulsar-nci-training-volume-to-pulsar-nci-training.device
}

output "worker_ip_addresses" {
  value = {
    for instance in openstack_compute_instance_v2.worker-nodes:
    instance.name => instance.access_ip_v4
  }
}
