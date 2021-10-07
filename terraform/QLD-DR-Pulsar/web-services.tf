# rabbitmq security group
resource "openstack_networking_secgroup_v2" "web-services" {
    name        = "Web-Services"
}

# icmp any port (check this!)
resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-icmp" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "icmp"
    security_group_id = "${openstack_networking_secgroup_v2.web-services.id}"
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-22" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 22
    port_range_min    = 22
    protocol          = "tcp"
    security_group_id = "${openstack_networking_secgroup_v2.web-services.id}"
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-80" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 80
    port_range_min    = 80
    protocol          = "tcp"
    security_group_id = "${openstack_networking_secgroup_v2.web-services.id}"
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-443" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 443
    port_range_min    = 443
    protocol          = "tcp"
    security_group_id = "${openstack_networking_secgroup_v2.web-services.id}"
}
