# openstack_compute_instance_v2.pulsar-QLD:
resource "openstack_compute_instance_v2" "pulsar-QLD" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-head"
    security_groups   = [
        "SSH only",
        "Web-Services",
        "default",
        "iperf",
        "pulsar_QLD_group",
        "rabbitmq",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-job-nfs:
resource "openstack_compute_instance_v2" "pulsar-QLD-job-nfs" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.8c24g"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-job-nfs"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-queue:
resource "openstack_compute_instance_v2" "pulsar-QLD-queue" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.8c24g"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-queue"
    security_groups   = [
        "SSH only",
        "Web-Services",
        "default",
        "pulsar_QLD_group",
        "rabbitmq",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w0:
resource "openstack_compute_instance_v2" "pulsar-QLD-w0" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w0"
    security_groups   = [
        "SSH only",
        "default",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w1:
resource "openstack_compute_instance_v2" "pulsar-QLD-w1" {
    availability_zone = "QRIScloud"
    flavor_name       = "qld.biocommons.16c64g"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w1"
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
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w2"
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
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w3"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w4:
resource "openstack_compute_instance_v2" "pulsar-QLD-w4" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w4"
    security_groups   = [
        "SSH only",
        "pulsar_QLD_group",
    ]
}

# openstack_compute_instance_v2.pulsar-QLD-w5:
resource "openstack_compute_instance_v2" "pulsar-QLD-w5" {
    availability_zone = "QRIScloud"
    flavor_name       = "r3.xlarge"
    image_id          = "bbac7966-fddc-4b31-9fb2-b4f09f4a7ae3"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w5"
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
    image_id          = "bbac7966-fddc-4b31-9fb2-b4f09f4a7ae3"
    key_pair          = "galaxy-australia"
    name              = "QLD-DR-w6"
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
    name              = "QLD-DR-head-web-app"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-job-nfs-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-job-nfs-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-job-nfs-volume"
    size              = 20000
}

#Volumes for workers
# openstack_blockstorage_volume_v2.pulsar-QLD-w0-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w0-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w0-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w1-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w1-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w1-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w2-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w2-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w2-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w3-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w3-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w3-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w4-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w4-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w4-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w5-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w5-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w5-volume"
    size              = 200
}

# openstack_blockstorage_volume_v2.pulsar-QLD-w6-volume:
resource "openstack_blockstorage_volume_v2" "pulsar-QLD-w6-volume" {
    availability_zone = "QRIScloud"
    name              = "QLD-DR-w6-volume"
    size              = 200
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-job-nfs-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-job-nfs.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-job-nfs-volume.id}"
}

resource "openstack_compute_volume_attach_v2" "attach-pulsar-QLD-w0-volume" {
  instance_id = "${openstack_compute_instance_v2.pulsar-QLD-w0.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-QLD-w0-volume.id}"
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

