# database
resource "openstack_compute_instance_v2" "pawsey-db" {
  name            = "pawsey-db"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

# application server / web server
resource "openstack_compute_instance_v2" "pawsey" {
  name            = "pawsey"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "Web-Services", "default"]
  availability_zone = "nova"
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "pawsey-queue" {
  name            = "pawsey-queue"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.4c16r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "default"]
  availability_zone = "nova"
}

# slurm worker
resource "openstack_compute_instance_v2" "pawsey-w1" {
  name            = "pawsey-w1"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

# slurm workers
resource "openstack_compute_instance_v2" "pawsey-w2" {
  name            = "pawsey-w2"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

resource "openstack_compute_instance_v2" "pawsey-w3" {
  name            = "pawsey-w3"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

resource "openstack_compute_instance_v2" "pawsey-w4" {
  name            = "pawsey-w4"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

resource "openstack_compute_instance_v2" "pawsey-w5" {
  name            = "pawsey-w5"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

resource "openstack_compute_instance_v2" "pawsey-w6" {
  name            = "pawsey-w6"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.32c128r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
}

## Volume for application/web server
#resource "openstack_blockstorage_volume_v2" "pawsey-volume" {
#  availability_zone = "nova"
#  name        = "pawsey-volume"
#  description = "Galaxy Australia Pawsey volume"
#  size        = 1200
#}
#
## Attachment between application/web server and volume
#resource "openstack_compute_volume_attach_v2" "attach-pawsey-volume-to-pawsey" {
#  instance_id = "${openstack_compute_instance_v2.pawsey.id}"
#  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-volume.id}"
#}
