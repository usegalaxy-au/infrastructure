resource "openstack_compute_instance_v2" "qld-pulsar-himem-0" {
    name              = "QLD-pulsar-himem-0"
    image_id          = "356ff1ed-5960-4ac2-96a1-0c0198e6a999"
    flavor_name       = "qld.biocommons.240c4000g"
    key_pair          = "galaxy-australia"
    security_groups   = [
        "SSH only",
        "default",
    ]
    availability_zone = "QRIScloud"
}

resource "openstack_blockstorage_volume_v2" "qld-pulsar-himem-0-volume" {
    name              = "QLD-himem-0-volume"
    availability_zone = "QRIScloud"
    size              = 10000
}

resource "openstack_compute_volume_attach_v2" "attach-qld-pulsar-himem-0-to-volume" {
  instance_id = "${openstack_compute_instance_v2.qld-pulsar-himem-0.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.qld-pulsar-himem-0-volume.id}"
}

resource "openstack_compute_instance_v2" "qld-pulsar-himem-1" {
    name              = "pulsar-qld-himem1"
    image_id          = "bbac7966-fddc-4b31-9fb2-b4f09f4a7ae3"
    flavor_name       = "qld.biocommons.240c4000g"
    key_pair          = "galaxy-australia"
    security_groups   = [
        "SSH only",
    ]
    availability_zone = "QRIScloud"
}

resource "openstack_blockstorage_volume_v2" "qld-pulsar-himem-1-volume" {
    name              = "QLD-himem-1-volume"
    availability_zone = "QRIScloud"
    size              = 10000
}

resource "openstack_compute_volume_attach_v2" "attach-qld-pulsar-himem-1-to-volume" {
  instance_id = "${openstack_compute_instance_v2.qld-pulsar-himem-1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.qld-pulsar-himem-1-volume.id}"
}

resource "openstack_compute_instance_v2" "qld-pulsar-himem-2" {
    name              = "pulsar-qld-himem2"
    image_id          = "bbac7966-fddc-4b31-9fb2-b4f09f4a7ae3"
    flavor_name       = "qld.biocommons.240c4000g"
    key_pair          = "galaxy-australia"
    security_groups   = [
        "SSH only",
    ]
    availability_zone = "QRIScloud"
}

resource "openstack_blockstorage_volume_v2" "qld-pulsar-himem-2-volume" {
    name              = "QLD-himem-2-volume"
    availability_zone = "QRIScloud"
    size              = 10000
}

resource "openstack_compute_volume_attach_v2" "attach-qld-pulsar-himem-2-to-volume" {
  instance_id = "${openstack_compute_instance_v2.qld-pulsar-himem-2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.qld-pulsar-himem-2-volume.id}"
}


