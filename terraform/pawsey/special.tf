# special security group
resource "openstack_networking_secgroup_v2" "special" {
    name        = "special"
}

resource "openstack_networking_secgroup_rule_v2" "rule_0-special" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "udp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "rule_1-special" {
    direction       = "ingress"
    ethertype       = "IPv6"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "tcp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "rule_3-special" {
    direction       = "ingress"
    ethertype       = "IPv6"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "udp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "rule_5-special" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "icmp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "rule_6-special" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "tcp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}
