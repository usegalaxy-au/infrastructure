resource "openstack_compute_instance_v2" "galactic-radio-telescope"{
  name            = "galactic-radio-telescope"
  image_id      = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "WEB-Services"]
  availability_zone = "melbourne-qh2"
}

# Volume for server
resource "openstack_blockstorage_volume_v2" "galactic-radio-telescope-volume" {
  availability_zone = "melbourne-qh2"
  name        = "galactic-radio-telescope-volume"
  description = "Galaxy Australia galactic-radio-telescope volume"
  size        = 100
}

# Attachment between server and volume
resource "openstack_compute_volume_attach_v2" "attach-galactic-radio-telescope-volume-to-galactic-radio-telescope" {
  instance_id = "${openstack_compute_instance_v2.galactic-radio-telescope.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.galactic-radio-telescope-volume.id}"
}
