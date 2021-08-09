locals {
  worker_count = 8
  tmp_disk_size = 200
  avail_zone = "QRIScloud"
  key_pair = "galaxy-australia"
  image_name = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"

  #Loops for worker nodes
  instances = toset(formatlist("%d", range(local.count)))
  volumes = toset(flatten([ for instance in local.instances : "i${instance}-volume" ]))
  attachments = toset(flatten([ for instance in local.instances : {
      instance = instance
      volume = "QLD-w${instance}-volume"
    }]))
}

######################################################################################
# Instances
######################################################################################

#Worker nodes
resource "openstack_compute_instance_v2" "worker-nodes" {
  for_each = local.instances
  name            = "QLD-w${each.value}"
  image_name      = local.image_name
  flavor_name     = "r3.xlarge"
  key_pair        = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}

#Head node
resource "openstack_compute_instance_v2" "QLD-head" {
  name = "QLD-Pulsar-DR"
  image_name = local.image_name
  flavor_name = "r3.large"
  key_pair = local.key_pair
  security_groups = ["SSH only", "Web-Services", "default"]
  availability_zone = local.avail_zone
}

#Queue server
resource "openstack_compute_instance_v2" "QLD-queue" {
  name = "QLD-queue"
  image_name = local.image_name
  flavor_name = "m3.medium"
  key_pair = local.key_pair
  security_groups = ["SSH only", "default", "rabbitmq"]
  availability_zone = local.avail_zone
}

#Job NFS
resource "openstack_compute_instance_v2" "QLD-job-nfs" {
  name = "QLD-job-nfs"
  image_name = local.image_name
  flavor_name = "r3.large"
  key_pair = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}

#Misc NFS
resource "openstack_compute_instance_v2" "QLD-misc-nfs" {
  name = "QLD-misc-nfs"
  image_name = local.image_name
  flavor_name = "r3.large"
  key_pair = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}

#Exports --- ##Commented out for now until we add it manually to the state file.
#resource "openstack_compute_instance_v2" "galaxy-aust-exports" {
  # name = "galaxy-aust-exports"
  # image_name = "NeCTAR Ubuntu 18.04 LTS (Bionic) amd64 [v29]"
  # flavor_name = "m3.large"
  # key_pair = "GenomicsVL 2019"
  # security_groups = ["default", "SSH only", "remote_nfs", "SLURM cluster"]
  # availability_zone = local.avail_zone
}

#Database server
resource "openstack_compute_instance_v2" "QLD-db" {
  name = "QLD-db"
  image_name = local.image_name
  flavor_name = "r3.medium"
  key_pair = local.key_pair
  security_groups = ["SSH only", "default"]
  availability_zone = local.avail_zone
}


######################################################################################
# Volumes
######################################################################################

# Worker volumes
resource "openstack_blockstorage_volume_v2" "worker_tmp_disk" {
  for_each = local.volumes
  availability_zone = local.avail_zone
  name        = each.value
  description = "Worker temp disk"
  size        = local.tmp_disk_size
}

#Head node volume
resource "openstack_compute_instance_v2" "QLD-pulsar-DR-volume" {
  availability_zone = local.avail_zone
  name = "QLD-pulsar-DR-volume"
  description = "Head node disk for server apps"
  size = 200
}

#Job nfs volume
resource "openstack_compute_instance_v2" "QLD-job-nfs-volume" {
  availability_zone = local.avail_zone
  name = "QLD-job-nfs-volume"
  description = "Job nfs volume for job tmps"
  size = 20000
}

#Misc nfs volume
resource "openstack_compute_instance_v2" "QLD-misc-nfs-volume" {
  availability_zone = local.avail_zone
  name = "QLD-misc-nfs-volume"
  description = "Job nfs volume for job tmps"
  size = 1000
}

#DB volume
resource "openstack_blockstorage_volume_v2" "QLD-db-volume" {
  availability_zone = local.avail_zone
  name = "QLD-db-volume"
  description = "Volume for replication DB server"
  size = 400
}


######################################################################################
# Attachments
######################################################################################

# Attachment between worker nodes and worker temp volumes
resource "openstack_compute_volume_attach_v2" "attach-worker-volume-to-worker" {
  for_each = { for idx in local.attachments: idx.instance => idx }
  instance_id = openstack_compute_instance_v2.worker-nodes[each.value.instance].id
  volume_id   = openstack_blockstorage_volume_v2.worker_tmp_disk[each.value.volume].id
}

# Attachment between Head node and head node volume
resource "openstack_compute_volume_attach_v2" "attach-QLD-pulsar-DR-volume-to-pulsar-DR" {
  instance_id = openstack_compute_instance_v2.QLD-head.id
  volume_id = openstack_blockstorage_volume_v2.QLD-pulsar-DR-volume.id
}

# Attachment between job nfs and job nfs volume
resource "openstack_compute_volume_attach_v2" "attach-QLD-job-nfs-volume-to-job-nfs" {
  instance_id = openstack_compute_instance_v2.QLD-job-nfs.id
  volume_id = openstack_blockstorage_volume_v2.QLD-job-nfs-volume.id
}

# Attachment between misc nfs and misc nfs volume
resource "openstack_compute_volume_attach_v2" "attach-QLD-misc-nfs-volume-to-misc-nfs" {
  instance_id = openstack_compute_instance_v2.QLD-misc-nfs.id
  volume_id = openstack_blockstorage_volume_v2.QLD-misc-nfs-volume.id
}

# Attachment between misc nfs and misc nfs volume
resource "openstack_compute_volume_attach_v2" "attach-QLD-db-volume-to-QLD-db" {
  instance_id = openstack_compute_instance_v2.QLD-db.id
  volume_id = openstack_blockstorage_volume_v2.QLD-db-volume.id
}

######################################################################################
# Outputs
######################################################################################

output "worker_ip_addresses" {
  value = {
    for instance in openstack_compute_instance_v2.worker-nodes:
    instance.id => instance.access_ip_v4
  }
}

output "worker volume devices" {
  value = {
    for instance in openstack_compute_instance_v2.worker_nodes:
    instance.id => openstack_compute_volume_attach_v2.attach-worker-volume-to-worker[each.value.instance_id].device
  }
}

output "head ip"{
  value = openstack_compute_instance_v2.QLD-head.access_ip_v4
}

output "Queue ip"{
  value = openstack_compute_instance_v2.QLD-queue.access_ip_v4
}

output "job nfs ip"{
  value = openstack_compute_instance_v2.QLD-job-nfs.access_ip_v4
}

output "misc nfs ip"{
  value = openstack_compute_instance_v2.QLD-misc-nfs.access_ip_v4
}

output "db ip"{
  value = openstack_compute_instance_v2.QLD-db.access_ip_v4
}
# output "volume_attachment" {
#   value = {
#     for volume in openstack_blockstorage_volume_v2.test-volume:
#     volume.id => volume.attachments
#   }
# }

