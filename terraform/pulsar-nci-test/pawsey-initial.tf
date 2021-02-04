# application server / web server
resource "openstack_compute_instance_v2" "pulsar-nci-test" {
  name            = "pulsar-nci-test"
  image_name      = "Ubuntu Focal Cloud Image 2020-05-28"
  flavor_name     = "c3.8c16m10d"
  key_pair        = "gvl_2019"
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
}

# worker nodes
resource "openstack_compute_instance_v2" "pulsar-nci-test-w1" {
  name            = "pulsar-nci-test-w1"
  image_name      = "Ubuntu Focal Cloud Image 2020-05-28"
  flavor_name     = "c3pl.16c48m60d"
  key_pair        = "gvl_2019"
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
}

resource "openstack_compute_instance_v2" "pulsar-nci-test-w2" {
  name            = "pulsar-nci-test-w2"
  image_name      = "Ubuntu Focal Cloud Image 2020-05-28"
  flavor_name     = "c3pl.16c48m60d"
  key_pair        = "gvl_2019"
  security_groups = ["ssh", "default"]
  availability_zone = "CloudV3"
  network {
    name = "aa63"
  }
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "pulsar-nci-test-volume" {
  availability_zone = "CloudV3"
  name        = "pulsar-nci-test-volume"
  description = "Pulsar NCI Test Volume"
  size        = 6000
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pulsar-nci-test-volume-to-pulsar-nci-test" {
  instance_id = "${openstack_compute_instance_v2.pulsar-nci-test.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-nci-test-volume.id}"
}

#floating ips for project
resource "openstack_networking_floatingip_v2" "floatip_head" {
  pool = "external"
}

resource "openstack_networking_floatingip_v2" "floatip_w1" {
  pool = "external"
}

resource "openstack_networking_floatingip_v2" "floatip_w2" {
  pool = "external"
}

#Associate FIPs with instances
resource "openstack_compute_floatingip_associate_v2" "fip_head" {
  floating_ip = "${openstack_networking_floatingip_v2.floatip_head.address}"
  instance_id = "${openstack_compute_instance_v2.pulsar-nci-test.id}"
}

resource "openstack_compute_floatingip_associate_v2" "fip_w1" {
  floating_ip = "${openstack_networking_floatingip_v2.floatip_w1.address}"
  instance_id = "${openstack_compute_instance_v2.pulsar-nci-test-w1.id}"
}

resource "openstack_compute_floatingip_associate_v2" "fip_w2" {
  floating_ip = "${openstack_networking_floatingip_v2.floatip_w2.address}"
  instance_id = "${openstack_compute_instance_v2.pulsar-nci-test-w2.id}"
}