# application server / web server
resource "openstack_compute_instance_v2" "pulsar-paw" {
  name            = "pulsar-paw"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "Web-Services", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# slurm worker
resource "openstack_compute_instance_v2" "pulsar-paw-w1" {
  name            = "pulsar-paw-w1"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# slurm worker
resource "openstack_compute_instance_v2" "pulsar-paw-w2" {
  name            = "pulsar-paw-w2"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# slurm worker
resource "openstack_compute_instance_v2" "pulsar-paw-w3" {
  name            = "pulsar-paw-w3"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# slurm worker
resource "openstack_compute_instance_v2" "pulsar-paw-w4" {
  name            = "pulsar-paw-w4"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# slurm worker
resource "openstack_compute_instance_v2" "pulsar-paw-w5" {
  name            = "pulsar-paw-w5"
  image_name      = "Pawsey - Ubuntu 20.04 - 2020-09-25"
  flavor_name     = "n3.8c32r"
  key_pair        = "gvl2019"
  security_groups = ["SSH", "default"]
  availability_zone = "nova"
  network {
    name = "Public external"
  }
  network {
    name = "galaxy-covid-19-network"
  }
}

# Volume for application/web server
resource "openstack_blockstorage_volume_v2" "pulsar-paw-volume" {
  availability_zone = "nova"
  name        = "pulsar-paw-volume"
  description = "Pulsar Pawsey volume"
  size        = 3000
}

# Attachment between application/web server and volume
resource "openstack_compute_volume_attach_v2" "attach-pulsar-paw-volume-to-pulsar-paw" {
  instance_id = "${openstack_compute_instance_v2.pulsar-paw.id}"
  volume_id   = "${openstack_blockstorage_volume_v2.pulsar-paw-volume.id}"
}
