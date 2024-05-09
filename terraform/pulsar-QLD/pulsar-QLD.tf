# openstack_compute_instance_v2.pulsar-QLD:
resource "openstack_compute_instance_v2" "pulsar-QLD" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD"
    security_groups   = [
        "SSH only",
        "Web-Services",
        "default",
        "iperf",
        "pulsar_QLD_group",
        "rabbitmq",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-nfs:
resource "openstack_compute_instance_v2" "pulsar-QLD-nfs" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.8c24g"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-nfs"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w1:
resource "openstack_compute_instance_v2" "pulsar-QLD-w1" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w1"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w2:
resource "openstack_compute_instance_v2" "pulsar-QLD-w2" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w2"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w3:
resource "openstack_compute_instance_v2" "pulsar-QLD-w3" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w3"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w4:
resource "openstack_compute_instance_v2" "pulsar-QLD-w4" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w4"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w5:
resource "openstack_compute_instance_v2" "pulsar-QLD-w5" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w5"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w6:
resource "openstack_compute_instance_v2" "pulsar-QLD-w6" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w6"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}


# openstack_compute_instance_v2.pulsar-QLD-w7:
resource "openstack_compute_instance_v2" "pulsar-QLD-w7" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7"
    key_pair          = "galaxy-australia"
    name              = "pulsar-QLD-w7"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}

# Volume for application/web server
# openstack_blockstorage_volume_v2.pulsar-QLD-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-volume"
    size              = 10000
}

# openstack_blockstorage_volume_v2.pulsar-QLD-job-nfs-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-nfs-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-nfs-volume"
    size              = 3000
}

#Volumes for workers
# openstack_blockstorage_volume_v2.pulsar-QLD-w1-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w1-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w1-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w2-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w2-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w2-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w3-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w3-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w3-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w4-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w4-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w4-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w5-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w5-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w5-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w6-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w6-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w6-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w7-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w7-volume" {
    availability_zone = "QRIScloud"
    name              = "pulsar-QLD-w7-volume"
    size              = 200
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-nfs-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-nfs.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-nfs-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w1-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w1-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w2-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w2-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w3-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w3.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w3-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w4-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w4.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w4-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w5-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w5.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w5-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w6-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w6.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w6-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w7-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w7.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w7-volume.id}"
}
