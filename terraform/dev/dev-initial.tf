# dev database
resource "openstack_compute_instance_v2" "dev-db" {
  name            = "dev-db"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "uom.general.2c8g"  # 2 vcpu 8 ram, previously m3.small (2 vcpu 4 ram)
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# application server / web server
resource "openstack_compute_instance_v2" "dev" {
  name            = "dev"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "uom.general.4c16g"  # previously m3.medium (4 vcpu 8 ram)
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "dev-queue" {
  name            = "dev-queue"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "uom.general.2c8g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "default"]
  availability_zone = "melbourne-qh2-uom"
}

# slurm workers
resource "openstack_compute_instance_v2" "dev-w1" {
  name            = "dev-w1"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "uom.general.16c64g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2-uom"
}

resource "openstack_compute_instance_v2" "dev-w2" {
  name            = "dev-w2"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
  flavor_name     = "uom.general.16c64g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2-uom"
}

#pulsar test server
resource "openstack_compute_instance_v2" "dev-pulsar" {
  name            = "dev-pulsar"
  image_id        = "f8b79936-6616-4a22-b55d-0d0a1d27bceb"
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

# Volumes for dev workers
resource "openstack_blockstorage_volume_v2" "dev-w1-volume" {
  availability_zone = "melbourne-qh2-uom"
  name        = "dev-w1-volume"
  description = "Galaxy Australia Dev w1 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "dev-w2-volume" {
  availability_zone = "melbourne-qh2-uom"
  name        = "dev-w2-volume"
  description = "Galaxy Australia Dev w2 volume"
  size        = 100
}

# Attachment between dev workers and volumes
resource "openstack_compute_volume_attach_v2" "attach-dev-w1-volume-to-dev-w1" {
  instance_id = "${openstack_compute_instance_v2.dev-w1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-w1-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-dev-w2-volume-to-dev-w2" {
  instance_id = "${openstack_compute_instance_v2.dev-w2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.dev-w2-volume.id}"
}
