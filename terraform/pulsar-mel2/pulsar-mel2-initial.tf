# Pulsar-mel2
resource "openstack_compute_instance_v2" "pulsar-mel2" {
  name            = "pulsar-mel2"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

#Workers
resource "openstack_compute_instance_v2" "pulsar-mel2-w1" {
  name            = "pulsar-mel2-w1"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w2" {
  name            = "pulsar-mel2-w2"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w3" {
  name            = "pulsar-mel2-w3"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w4" {
  name            = "pulsar-mel2-w4"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w5" {
  name            = "pulsar-mel2-w5"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w6" {
  name            = "pulsar-mel2-w6"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

resource "openstack_compute_instance_v2" "pulsar-mel2-w7" {
  name            = "pulsar-mel2-w7"
  image_id        = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
  flavor_name     = "r3.large"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "pulsar-mel2-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-volume"
  description = "Pulsar-mel2 volume"
  size        = 8000
}

#Volumes for workers
resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w1-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w1-volume"
  description = "Pulsar-mel2 W1 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w2-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w2-volume"
  description = "Pulsar-mel2 W2 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w3-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w3-volume"
  description = "Pulsar-mel2 W3 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w4-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w4-volume"
  description = "Pulsar-mel2 W4 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w5-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w5-volume"
  description = "Pulsar-mel2 W5 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w6-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w6-volume"
  description = "Pulsar-mel2 W6 volume"
  size        = 100
}

resource "openstack_blockstorage_volume_v2" "pulsar-mel2-w7-volume" {
  availability_zone = "melbourne-qh2"
  name        = "pulsar-mel2-w7-volume"
  description = "Pulsar-mel2 W7 volume"
  size        = 100
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-mel2-volume-to-mel2" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w1-volume-to-mel2-w1" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w1-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w2-volume-to-mel2-w2" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w2-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w3-volume-to-mel2-w3" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w3.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w3-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w4-volume-to-mel2-w4" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w4.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w4-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w5-volume-to-mel2-w5" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w5.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w5-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w6-volume-to-mel2-w6" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w6.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w6-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-mel2-w7-volume-to-mel2-w7" {
  instance_id = "${openstack_compute_instance_v2.pulsar-mel2-w7.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-mel2-w7-volume.id}"
}
