# Pulsar-mel2
resource "openstack_compute_instance_v2" "pulsar-high-mem1" {
  name            = "pulsar-high-mem1"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "uom.biocommons.252c4000g"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}
