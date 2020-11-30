

# slurm worker
resource "openstack_compute_instance_v2" "pawsey-w1" {
  name            = "pawsey-w1"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}


# Backup VM - performs database backups
resource "openstack_compute_instance_v2" "pawsey-backup" {
  name            = "pawsey-backup"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.2c8r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}


# tmp volumes for worker nodes
resource "openstack_blockstorage_volume_v2" "pawsey-w1-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w1-tmp"
  description = "tmp volume for w1"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w1-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w1-tmp.id}"
}

# Volume for backup server
resource "openstack_blockstorage_volume_v2" "pawsey-backup-vol" {
  availability_zone = "nova"
  name        = "pawsey-backup-vol"
  description = "Galaxy user data"
  size        = 500
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-backup-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-backup.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-backup-vol.id}"
}
