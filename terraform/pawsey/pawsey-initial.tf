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
  security_groups = ["SSH", "Web-Services", "default"]
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

# slurm workers
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

resource "openstack_compute_instance_v2" "pawsey-w6" {
  name            = "pawsey-w6"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.32c128r"
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
resource "openstack_compute_volume_attach_v2" "attach-pawsey-db-volume-to-pawsey-db" {
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
resource "openstack_compute_volume_attach_v2" "attach-pawsey-volume-to-pawsey" {
  instance_id = "${openstack_compute_instance_v2.pawsey.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-volume.id}"
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

resource "openstack_blockstorage_volume_v2" "pawsey-w2-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w2-tmp"
  description = "tmp volume for w2"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w2-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w2.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w2-tmp.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w3-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w3-tmp"
  description = "tmp volume for w3"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w3-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w3.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w3-tmp.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w4-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w4-tmp"
  description = "tmp volume for w4"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w4-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w4.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w4-tmp.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w5-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w5-tmp"
  description = "tmp volume for w5"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w5-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w5.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w5-tmp.id}"
}

resource "openstack_blockstorage_volume_v2" "pawsey-w6-tmp" {
  availability_zone = "nova"
  name        = "pawsey-w6-tmp"
  description = "tmp volume for w6"
  size        = 100
}

resource "openstack_compute_volume_attach_v2" "attach-pawsey-w6-tmp-volume" {
  instance_id = "${openstack_compute_instance_v2.pawsey-w6.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pawsey-w6-tmp.id}"
}
