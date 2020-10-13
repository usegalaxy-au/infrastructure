# galaxy-staging-db security group
resource "openstack_networking_secgroup_v2" "galaxy-staging-db" {
    description = "Security group for the galaxy australia staging server and it's own db server"
    name        = "galaxy-staging-db"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-staging-db-ingress-staging-5432" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 5432
    port_range_min    = 5432
    protocol          = "tcp"
    remote_ip_prefix  = "${openstack_compute_instance_v2.staging.network[0].fixed_ip_v4}/0"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-staging-db.id}"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-staging-db-ingress-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-staging-db.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-staging-db.id}"
}

# galaxy-staging security group
resource "openstack_networking_secgroup_v2" "galaxy-staging" {
    description = "Security group for all machines in the Galaxy Australia staging server ecosystem"
    name        = "galaxy-staging"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-staging-ingress-tcp-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-staging.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-staging.id}"
}

resource "openstack_networking_secgroup_rule_v2" "galaxy-staging-ingress-udp-group" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "udp"
    remote_group_id   = "${openstack_networking_secgroup_v2.galaxy-staging.id}"
    security_group_id = "${openstack_networking_secgroup_v2.galaxy-staging.id}"
}
