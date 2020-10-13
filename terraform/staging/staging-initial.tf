# staging database
resource "openstack_compute_instance_v2" "staging-db" {
  name            = "staging-db"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-staging-db.name}"]
  availability_zone = "melbourne-qh2"
}

# application server / web server
resource "openstack_compute_instance_v2" "staging" {
  name            = "staging"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "${openstack_networking_secgroup_v2.galaxy-staging.name}", "${openstack_networking_secgroup_v2.galaxy-staging-db.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "staging-queue" {
  name            = "staging-queue"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "${openstack_networking_secgroup_v2.galaxy-staging.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm worker
resource "openstack_compute_instance_v2" "staging-w1" {
  name            = "staging-w1"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.large"  # intended to be c3.xlarge
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-staging.name}"]
  availability_zone = "melbourne-qh2"
}

# pulsar test server
resource "openstack_compute_instance_v2" "staging-pulsar" {
  name            = "staging-pulsar"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
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
