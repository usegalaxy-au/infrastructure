# rabbitMQ
resource "openstack_compute_instance_v2" "prod-rabbit" {
  name            = "prod-rabbit"
  image_name      = "NeCTAR Ubuntu 20.04 LTS (Focal) amd64"
  flavor_name     = "m3.small"
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "Web-Services", "rabbitmq"]
  availability_zone = "melbourne-qh2"
}