# dev database
resource "openstack_compute_instance_v2" "dev-db" {
  name            = "dev-db"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64 [v3]"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-dev-db.name}"]
  availability_zone = "melbourne-qh2"
}

# application server / web server
resource "openstack_compute_instance_v2" "dev" {
  name            = "dev"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64 [v3]"
  flavor_name     = "m3.medium"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "${openstack_networking_secgroup_v2.galaxy-dev.name}", "${openstack_networking_secgroup_v2.galaxy-dev-db.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "dev-queue" {
  name            = "dev-queue"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64 [v3]"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "${openstack_networking_secgroup_v2.galaxy-dev.name}"]
  availability_zone = "melbourne-qh2"
}

# slurm worker
resource "openstack_compute_instance_v2" "dev-w1" {
  name            = "dev-w1"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64 [v3]"
  flavor_name     = "m3.medium"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "${openstack_networking_secgroup_v2.galaxy-dev.name}"]
  availability_zone = "melbourne-qh2"
}

#pulsar test server
resource "openstack_compute_instance_v2" "dev-pulsar" {
  name            = "dev-pulsar"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64 [v3]"
  flavor_name     = "m3.medium"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH"]
  availability_zone = "melbourne-qh2"
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "dev-volume" {
  availability_zone = "melbourne-qh2"
  name        = "dev-volume"
  description = "Galaxy Australia Dev volume"
  size        = 200
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-dev-volume-to-dev" {
  instance_id = "${openstack_compute_instance_v2.dev.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-volume.id}"
}

# Volume for upload store
resource "openstack_blockstorage_volume_v2" "dev-upload-store-volume" {
  availability_zone = "melbourne-qh2"
  name        = "dev-upload-store-volume"
  description = "Galaxy Australia Dev volume for upload store"
  size        = 200
}

# Attachment between application/web server and upload store volume
resource "openstack_compute_volume_attach_v2" "attach-dev-upload-store-volume-to-dev" {
  instance_id = "${openstack_compute_instance_v2.dev.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-upload-store-volume.id}"
}