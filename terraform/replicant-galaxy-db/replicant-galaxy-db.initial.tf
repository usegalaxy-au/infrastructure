# replicant-galaxy-db VM
resource "openstack_compute_instance_v2" "replicant-galaxy-db" {
  name            = "replicant-galaxy-db"
  image_id        = "7eb4ff70-8a91-4f66-b424-d0b9b551a252"  # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name     = "r3.medium"  # 4CPU, 16GB. Is this too stingy? Can always resize
  key_pair        = "galaxy-australia"
  security_groups = ["SSH", "default"]
  availability_zone = "melbourne-qh2"
}

# Volume
resource "openstack_blockstorage_volume_v3" "replicant-galaxy-db-volume" {
  availability_zone = "melbourne-qh2"
  name        = "replicant-galaxy-db-volume"
  description = "Replicant Galaxy DB volume"
  size        = 400
}

# Attachment between server and volume
resource "openstack_compute_volume_attach_v2" "attach-dev-volume-to-dev" {
  instance_id = "${openstack_compute_instance_v2.replicant-galaxy-db.id}"
  volume_id   = "${openstack_blockstorage_volume_v3.replicant-galaxy-db-volume.id}"
}