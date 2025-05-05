# Build server
resource "openstack_compute_instance_v2" "nci-build" {
  name            = "nci-build"
  image_id        = "b6f837e1-49fe-495d-905a-f4ddb2f6b669" # Ubuntu Jammy Cloud Image 2023-02-15
  flavor_name     = "c3.2c4m10d"
  key_pair        = "galaxy-australia"
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
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
