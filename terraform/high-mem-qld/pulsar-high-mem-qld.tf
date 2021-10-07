locals {
  worker_count = 3
  tmp_disk_size = 10000
  avail_zone = "QRIScloud"
  key_pair = "galaxy-australia"
  image_name = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name  = "qld.biocommons.240c4000g"

  #Loops for worker nodes
  instances = toset(formatlist("%d", range(local.worker_count)))
  volumes = toset(flatten([ for instance in local.instances : "QLD-high-mem-${instance}-volume" ]))
  attachments = toset(flatten([ for instance in local.instances : {
      instance = instance
      volume = "QLD-high-mem-${instance}-volume"
    }]))
}

######################################################################################
# Instances
######################################################################################

#himem nodes
resource "openstack_compute_instance_v2" "himem-nodes"{
  for_each = local.instances
  name            = "QLD-pulsar-himem-${each.value}"
  image_name      = local.image_name
  flavor_name     = local.flavor_name
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}
