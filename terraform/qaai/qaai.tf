# QA AI database server
resource "openstack_compute_instance_v2" "qaai-db" {
  name              = "qaai-db"
  image_id          = "c0250c96-98a4-4bfa-b67c-51874808337f"  # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "r3.large"  # 8c/32g
  # flavor_name       = "r3.xsmall"
  key_pair          = "galaxy-australia"
  security_groups   = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

# QA AI application / web server
resource "openstack_compute_instance_v2" "qaai" {
  name              = "qaai"
  image_id          = "c0250c96-98a4-4bfa-b67c-51874808337f"  # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "r3.xlarge"  # 16c/64g
  # flavor_name       = "r3.xsmall"
  key_pair          = "galaxy-australia"
  security_groups   = ["SSH", "Web-Services", "default"]
  availability_zone = "melbourne-qh2"
}

# Volume for the QA AI database server
resource "openstack_blockstorage_volume_v3" "qaai-db-volume" {
  availability_zone = "melbourne-qh2"
  name        = "qaai-db-volume"
  description = "QA AI database volume"
  size        = 500
}

# Volume for the QA AI application server
resource "openstack_blockstorage_volume_v3" "qaai-volume" {
  availability_zone = "melbourne-qh2"
  name        = "qaai-volume"
  description = "QA AI application volume"
  size        = 1000
}

# Attach volumes to instances
resource "openstack_compute_volume_attach_v2" "attach-qaai-db-volume" {
  instance_id = openstack_compute_instance_v2.qaai-db.id
  volume_id   = openstack_blockstorage_volume_v3.qaai-db-volume.id
}

resource "openstack_compute_volume_attach_v2" "attach-qaai-volume" {
  instance_id = openstack_compute_instance_v2.qaai.id
  volume_id   = openstack_blockstorage_volume_v3.qaai-volume.id
}
