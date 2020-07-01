# dev database
resource "openstack_compute_instance_v2" "dev-db" {
  name            = "dev-db"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "galaxy-dev-db"]
  availability_zone = "melbourne-qh2"
}

# application server / web server
resource "openstack_compute_instance_v2" "dev" {
  name            = "dev"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.medium"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "galaxy-dev", "galaxy-dev-db"]
  availability_zone = "melbourne-qh2"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "dev-queue" {
  name            = "dev-queue"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "galaxy-dev"]
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
