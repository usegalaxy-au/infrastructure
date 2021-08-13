locals {
  worker_count = 3
  tmp_disk_size = 200
  avail_zone = "QRIScloud"
  key_pair = "galaxy-australia"
  image_name = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"

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
# qld-pulsar-high-mem-1
resource "openstack_compute_instance_v2" "qld-pulsar-high-mem-1" {
  name            = "qld-pulsar-high-mem-1"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "qld.biocommons.240c4000g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "QRIScloud"
}

# qld-pulsar-high-mem-2
resource "openstack_compute_instance_v2" "qld-pulsar-high-mem-1" {
  name            = "qld-pulsar-high-mem-2"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "qld.biocommons.240c4000g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "QRIScloud"
}

# qld-pulsar-high-mem-3
resource "openstack_compute_instance_v2" "qld-pulsar-high-mem-3" {
  name            = "qld-pulsar-high-mem-3"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "qld.biocommons.240c4000g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "QRIScloud"
}
