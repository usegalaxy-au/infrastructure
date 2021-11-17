locals {
  avail_zone = "QRIScloud"
  key_pair = "galaxy-australia"
  image_name = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  default_flavor_name = "qld.biocommons.8c24g"

  private_ip = "qld-data"
  public_ip = "qld"

  worker_count = 3
  worker_flavor_name = "qld.biocommons.16c64g"
  tmp_disk_size = 100

  #Loops for hybrid worker nodes
  instances = toset(formatlist("%d", range(local.worker_count)))
  volumes = toset(flatten([ for instance in local.instances : "QLD-DR-w${instance}-volume" ]))
  attachments = toset(flatten([ for instance in local.instances : {
      instance = instance
      volume = "QLD-DR-w${instance}-volume"
    }]))
}


######################################################################################
# Instances
######################################################################################

# hybrid DR-pulsar worker nodes
resource "openstack_compute_instance_v2" "QLD-DR-w"{
  for_each = local.instances
  name            = "QLD-DR-w${each.value}"
  image_name      = local.image_name
  flavor_name     = local.worker_flavor_name
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}

# QLD-DR-Galaxy-Head
resource "openstack_compute_instance_v2" "QLD-DR-head" {
  name            = "QLD-DR-head"
  image_name      = local.image_name
  flavor_name     = "qld.biocommons.16c64g"
  key_pair        = local.key_pair
  security_groups = ["SSH only", "Web-Services", "rabbitmq", "default"]
  availability_zone = local.avail_zone
  network {
    name = local.private_ip
  }
  network {
    name = local.public_ip
  }
}

# QLD-DR-db database
resource "openstack_compute_instance_v2" "QLD-DR-db" {
  name            = "QLD-DR-db"
  image_name      = local.image_name
  flavor_name     = "qld.biocommons.8c24g"
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
  network {
    name = local.public_ip
  }
  network {
    name = local.private_ip
  }
}

# Qld-DR-job-nfs
resource "openstack_compute_instance_v2" "QLD-DR-job-nfs" {
  name            = "QLD-DR-job-nfs"
  image_name      = local.image_name
  flavor_name     = local.default_flavor_name
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
  network {
    name = local.public_ip
  }
  network {
    name = local.private_ip
  }
}


# Qld-DR-queue
resource "openstack_compute_instance_v2" "QLD-DR-queue" {
  name            = "QLD-DR-queue"
  image_name      = local.image_name
  flavor_name     = local.default_flavor_name
  key_pair        = local.key_pair
  security_groups = ["SSH only", "Web-Services", "rabbitmq", "default"]
  availability_zone = local.avail_zone
  network {
    name = local.public_ip
  }
  network {
    name = local.private_ip
  }
}

######################################################################################
# Volumes
######################################################################################

# hybrid node temp volumes
resource "openstack_blockstorage_volume_v2" "hybrid_worker_node_tmp_disk" {
  for_each = local.volumes
  availability_zone = local.avail_zone
  name        = each.value
  description = "hybrid worker node temp disk"
  size        = local.tmp_disk_size
}

######################################################################################
# Attachments
######################################################################################

# Attachment between hybrid worker nodes and their temp volumes
resource "openstack_compute_volume_attach_v2" "attach-tmp-volume-to-hybrid_worker" {
  for_each = { for idx in local.attachments: idx.instance => idx }
  instance_id = openstack_compute_instance_v2.QLD-DR-w[each.value.instance].id
  volume_id   = openstack_blockstorage_volume_v2.hybrid_worker_node_tmp_disk[each.value.volume].id
}


