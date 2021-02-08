# special security group
resource "openstack_networking_secgroup_v2" "special" {
    name        = "special"
}

resource "openstack_networking_secgroup_rule_v2" "special-ingress-ipv4-udp-self-referencing" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "udp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "special-ingress-ipv6-tcp-self-referencing" {
    direction       = "ingress"
    ethertype       = "IPv6"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "tcp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "special-ingress-ipv6-udp-self-referencing" {
    direction       = "ingress"
    ethertype       = "IPv6"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "udp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "special-ingress-ipv4-icmp-self-referencing" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "icmp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}

resource "openstack_networking_secgroup_rule_v2" "special-ingress-ipv4-tcp-self-referencing" {
    direction       = "ingress"
    ethertype       = "IPv4"
    port_range_max  = 0
    port_range_min  = 0
    protocol        = "tcp"
    remote_group_id = "${openstack_networking_secgroup_v2.special.id}"
    security_group_id = "${openstack_networking_secgroup_v2.special.id}"
}
