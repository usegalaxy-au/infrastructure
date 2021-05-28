# dev database
resource "openstack_compute_instance_v2" "dev-db" {
  name            = "dev-db"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.2c8g"  # 2 vcpu 8 ram, previously m3.small (2 vcpu 4 ram)
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# application server / web server
resource "openstack_compute_instance_v2" "dev" {
  name            = "dev"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.4c16g"  # previously m3.medium (4 vcpu 8 ram)
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "dev-queue" {
  name            = "dev-queue"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.2c8g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# slurm worker
resource "openstack_compute_instance_v2" "dev-w1" {
  name            = "dev-w1"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.4c16g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2-uom"
}

#pulsar test server
resource "openstack_compute_instance_v2" "dev-pulsar" {
  name            = "dev-pulsar"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.2c8g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH"]
  availability_zone = "melbourne-qh2-uom"
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "dev-volume" {
  availability_zone = "melbourne-qh2-uom"
  name        = "dev-volume"
  description = "Galaxy Australia Dev volume"
  size        = 1000
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-dev-volume-to-dev" {
  instance_id = "${openstack_compute_instance_v2.dev.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-volume.id}"
}

# ftp
resource "openstack_compute_instance_v2" "dev-ftp" {
  name            = "dev-ftp"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.general.2c8g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# Volume for ftp
resource "openstack_blockstorage_volume_v2" "dev-ftp-volume" {
  availability_zone = "melbourne-qh2-uom"
  name        = "dev-ftp-volume"
  description = "Galaxy Australia Dev volume for ftp"
  size        = 300
}

# Attachment between application/web server and upload store volume
resource "openstack_compute_volume_attach_v2" "attach-dev-ftp-volume-to-dev-ftp" {
  instance_id = "${openstack_compute_instance_v2.dev-ftp.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-ftp-volume.id}"
}

