locals {
  worker_count = 3
  tmp_disk_size = 10000
  avail_zone = "QRIScloud"
  key_pair = "galaxy-australia"
  image_name = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name  = "qld.biocommons.240c4000g"
#  flavor_name = "qld.biocommons.8c24g"

  #Loops for worker nodes
  instances = toset(formatlist("%d", range(local.worker_count)))
  volumes = toset(flatten([ for instance in local.instances : "QLD-himem-${instance}-volume" ]))
  attachments = toset(flatten([ for instance in local.instances : {
      instance = instance
      volume = "QLD-himem-${instance}-volume"
    }]))
}

######################################################################################
# Instances
######################################################################################

#himem nodes
resource "openstack_compute_instance_v2" "QLD-pulsar-himem"{
  for_each = local.instances
  name            = "QLD-pulsar-himem-${each.value}"
  image_name      = local.image_name
  flavor_name     = local.flavor_name
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}

######################################################################################
# Volumes
######################################################################################

# himem temp volumes
resource "openstack_blockstorage_volume_v2" "himem_tmp_disk" {
  for_each = local.volumes
  availability_zone = local.avail_zone
  name        = each.value
  description = "himem tmp disk"
  size        = local.tmp_disk_size
}

######################################################################################
# Attachments
######################################################################################

# Attachment between nodes and himem temp volumes
resource "openstack_compute_volume_attach_v2" "attach-himem-tmp-volume-to-himem" {
  for_each = { for idx in local.attachments: idx.instance => idx }
  instance_id = openstack_compute_instance_v2.QLD-pulsar-himem[each.value.instance].id
  volume_id   = openstack_blockstorage_volume_v2.himem_tmp_disk[each.value.volume].id
}
