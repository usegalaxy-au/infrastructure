# database
resource "openstack_compute_instance_v2" "pawsey-db" {
  name            = "pawsey-db"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
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

# application server / web server
resource "openstack_compute_instance_v2" "pawsey" {
  name            = "pawsey"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "Web-Services", "default", "special"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "pawsey-queue" {
  name            = "pawsey-queue"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.4c16r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

resource "openstack_compute_instance_v2" "pawsey-queue2" {
  name  = "pawsey-queue2"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name = "n3.4c16r"
  key_pair    = "gvl2019"
  security_groups = ["SSH", "Web-Services", "rabbitmq", "default", "special"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

# slurm workers
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

resource "openstack_compute_instance_v2" "pawsey-w2" {
  name            = "pawsey-w2"
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

resource "openstack_compute_instance_v2" "pawsey-w3" {
  name            = "pawsey-w3"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

resource "openstack_compute_instance_v2" "pawsey-w4" {
  name            = "pawsey-w4"
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

resource "openstack_compute_instance_v2" "pawsey-w5" {
  name            = "pawsey-w5"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

resource "openstack_compute_instance_v2" "pawsey-w6" {
  name            = "pawsey-w6"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name     = "n3.32c128r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

resource "openstack_compute_instance_v2" "pawsey-w7" {
  name            = "pawsey-w7"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name     = "n3.16c64r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-genomics-network"
  }
}

# nfs machines
resource "openstack_compute_instance_v2" "pawsey-misc-nfs" {
  name            = "pawsey-misc-nfs"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
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

resource "openstack_compute_instance_v2" "pawsey-job-nfs" {
  name            = "pawsey-job-nfs"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
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

resource "openstack_compute_instance_v2" "pawsey-user-nfs" {
  name            = "pawsey-user-nfs"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
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

resource "openstack_compute_instance_v2" "pawsey-user-nfs-2" {
  name = "pawsey-user-nfs-2"
  image_name  = null  ### set image name for new instances created with terraform
  flavor_name = "n3.8c32r"
  key_pair  = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  block_device {  ### only for new pawsey machines created while terraform was unavailable
    uuid = "61c78971-fee5-4d25-b86b-067f3646ef11"
    source_type = "image"
    boot_index   = 0
    delete_on_termination = true
    destination_type  = "volume"
    volume_size      = 40
  }
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

# Volume for database server
resource "openstack_blockstorage_volume_v2" "pawsey-db-volume" {
 availability_zone = "nova"
 name        = "pawsey-db-volume"
 description = "Galaxy Australia Pawsey database volume"
 size        = 200
}

# Attachment between db server and volume
resource "openstack_compute_volume_attach_v2" "attach-pawsey-db-volume" {
 instance_id = "${openstack_compute_instance_v2.pawsey-db.id}"
 volume_id   = "${openstack_blockstorage_volume_v2.pawsey-db-volume.id}"
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "pawsey-volume" {
  availability_zone = "nova"
  name        = "pawsey-volume"
  description = "Galaxy Australia Pawsey volume"
  size        = 500
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pawsey-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-volume.id}"
}

# tmp volumes for worker nodes
resource "openstack_blockstorage_volume_v2" "pawsey-w1-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w1-tmp-new"
  description = "tmp vol for pawsey-w1"
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w1-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w1.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w1-tmp-new.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w2-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w2-tmp-new"
  description = "new tmp vol for w2"
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w2-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w2-tmp-new.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w3-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w3-tmp-new"
  description = ""
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w3-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w3.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w3-tmp-new.id}"
}


resource "openstack_blockstorage_volume_v2" "pawsey-w4-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w4-tmp-new"
  description = "new tmp vol for w4"
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w4-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w4.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w4-tmp-new.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w5-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w5-tmp-new"
  description = "New tmp for w5"
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w5-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w5.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w5-tmp-new.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w6-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w6-tmp-new"
  description = "new tmp vol for w6"
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w6-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w6.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w6-tmp-new.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w7-tmp-new" {
  availability_zone = "nova"
  name        = "pawsey-w7-tmp-new"
  description = ""
  size        = 200
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w7-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w7.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w7-tmp-new.id}"
}

# Volumes for nfs servers
resource "openstack_blockstorage_volume_v2" "pawsey-misc-nfs-vol" {
  availability_zone = "nova"
  name        = "pawsey-misc-nfs-vol"
  description = "ghostapp, tools and custom indices volume"
  size        = 1000
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-misc-nfs-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-misc-nfs.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-misc-nfs-vol.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-job-nfs-vol" {
  availability_zone = "nova"
  name        = "pawsey-misc-job-vol"
  description = "Jobs working directories and galaxy tmp"
  size        = 20000
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-job-nfs-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-job-nfs.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-job-nfs-vol.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-user-nfs-vol" {
  availability_zone = "nova"
  name        = "pawsey-user-nfs-vol"
  description = "Galaxy user data"
  size        = 70000
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-user-nfs-2-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-user-nfs-2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-user-nfs-vol.id}"
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
