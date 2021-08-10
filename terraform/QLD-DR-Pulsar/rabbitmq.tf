# rabbitmq security group
resource "openstack_networking_secgroup_v2" "rabbitmq" {
    name        = "rabbitmq"
}

resource "openstack_networking_secgroup_rule_v2" "rabbitmq-ingress-tcp-5671" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 5671
    port_range_min    = 5671
    protocol          = "tcp"
    security_group_id = openstack_networking_secgroup_v2.rabbitmq.id
}

resource "openstack_networking_secgroup_rule_v2" "rabbitmq-ingress-udp-5671" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 5671
    port_range_min    = 5671
    protocol          = "udp"
    security_group_id = openstack_networking_secgroup_v2.rabbitmq.id
}
