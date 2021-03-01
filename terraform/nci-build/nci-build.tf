# Build server
resource "openstack_compute_instance_v2" "nci-build" {
  name            = "nci-build"
  image_name      = "Ubuntu Focal Cloud Image 2020-05-28"
  flavor_name     = "c3.2c4m10d"
  key_pair        = "gvl_2019"
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "nci-build-volume" {
  availability_zone = "CloudV3"
  name        = "nci-build-volume"
  description = "NCI Build Machine Volume"
  size        = 200
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-nci-build-volume-to--nci-build" {
  instance_id = "${openstack_compute_instance_v2.nci-build.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.nci-build-volume.id}"
}

#floating ips for project
resource "openstack_networking_floatingip_v2" "floatip_build" {
  pool = "external"
}

#Associate FIPs with instances
resource "openstack_compute_floatingip_associate_v2" "fip_build" {
  floating_ip = "${openstack_networking_floatingip_v2.floatip_build.address}"
  instance_id = "${openstack_compute_instance_v2.nci-build.id}"
}
