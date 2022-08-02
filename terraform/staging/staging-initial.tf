# August 3, 2022
# The state file is somehow out of whack for this project and calls to `terraform plan` result in terraform planning
# to double up the VMs that already exist in the state
# This could be fixed by:
# (1) throwing away the state file
# (2) using `terraform import` to repopulate the state file with the existing instances/volumes/attachments
# (3) deleting the custom security groups and using "default" instead
# instances to reimport are
# - VMs: staging, staging-db, staging-pulsar, staging-queue, staging-w1
# - Volumes: 1200 for staging, 100 for staging-w1
# - Attachments between VMs and volumes

# staging database
resource "openstack_compute_instance_v2" "staging-db" {
  name            = "staging-db"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-staging-db.name}"]
  availability_zone = "melbourne-qh2"
}

# application server / web server
resource "openstack_compute_instance_v2" "staging" {
  name            = "staging"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "m3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "${openstack_networking_secgroup_v2.galaxy-staging.name}", "${openstack_networking_secgroup_v2.galaxy-staging-db.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "staging-queue" {
  name            = "staging-queue"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "${openstack_networking_secgroup_v2.galaxy-staging.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm worker
resource "openstack_compute_instance_v2" "staging-w1" {
  name            = "staging-w1"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "m3.large"  # intended to be c3.xlarge
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-staging.name}"]
  availability_zone = "melbourne-qh2"
}

# pulsar test server
resource "openstack_compute_instance_v2" "staging-pulsar" {
  name            = "staging-pulsar"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH"]
  availability_zone = "melbourne-qh2"
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "staging-volume" {
  availability_zone = "melbourne-qh2"
  name        = "staging-volume"
  description = "Galaxy Australia Staging volume"
  size        = 1200
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-staging-volume-to-staging" {
  instance_id = "${openstack_compute_instance_v2.staging.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.staging-volume.id}"
}
