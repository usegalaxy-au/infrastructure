# galaxy-dev-db security group
resource "openstack_networking_secgroup_v2" "galaxy-dev-db" {
    description = "Security group for the galaxy australia development server and it's own db server"
    name        = "galaxy-dev-db"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-dev-db-ingress-dev-5432" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 5432
    port_range_min    = 5432
    protocol          = "tcp"
    remote_ip_prefix  = "${openstack_compute_instance_v2.dev.network[0].fixed_ip_v4}/0"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-dev-db.id}"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-dev-db-ingress-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-dev-db.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-dev-db.id}"
}

# galaxy-dev security group
resource "openstack_networking_secgroup_v2" "galaxy-dev" {
    description = "Security group for all machines in the Galaxy Australia Development server ecosystem"
    name        = "galaxy-dev"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-dev-ingress-tcp-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-dev.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-dev.id}"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-dev-ingress-udp-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "udp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-dev.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-dev.id}"
}
