# internal network
resource "openstack_networking_network_v2" "network" {
  name = "galaxy-int-net"
}

resource "openstack_networking_subnet_v2" "subnet" {
  name       = "galaxy-int-subnet"
  network_id = openstack_networking_network_v2.network.id
  cidr       = "192.168.0.0/24"
  ip_version = 4
}

# ssh-icmp security group
resource "openstack_networking_secgroup_v2" "ssh-icmp" {
  name        = "SSH-ICMP"
  description = "SSH and ICMP security group"
}

resource "openstack_networking_secgroup_rule_v2" "ingress-ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.ssh-icmp.id
}

resource "openstack_networking_secgroup_rule_v2" "ingress-icmp" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.ssh-icmp.id
}

# web security group
resource "openstack_networking_secgroup_v2" "web-services" {
    name        = "Web-Services"
}

# icmp any port 
resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-icmp" {
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "icmp"
    security_group_id = openstack_networking_secgroup_v2.web-services.id
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-22" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 22
    port_range_min    = 22
    protocol          = "tcp"
    security_group_id = openstack_networking_secgroup_v2.web-services.id
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-80" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 80
    port_range_min    = 80
    protocol          = "tcp"
    security_group_id = openstack_networking_secgroup_v2.web-services.id
}

resource "openstack_networking_secgroup_rule_v2" "web-services-ingress-tcp-443" {
    direction         = "ingress"
    ethertype         = "IPv4"
    port_range_max    = 443
    port_range_min    = 443
    protocol          = "tcp"
    security_group_id = openstack_networking_secgroup_v2.web-services.id
}

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
