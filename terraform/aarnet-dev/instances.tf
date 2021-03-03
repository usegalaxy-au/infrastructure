# SSH-ICMP KEY CREATION
resource "openstack_compute_keypair_v2" "galaxy-dev-key" {
  name = "galaxy-dev-key"
}

# ansible
resource "openstack_compute_instance_v2" "aarnet-ansible" {
  name            = "aarnet-ansible"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "c2647963-8151-4df9-bd22-1787e022412b" # m1.medium
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}

# database
resource "openstack_compute_instance_v2" "aarnet-db" {
  name            = "aarnet-db"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "70ff51f7-0edb-413b-b548-0048bfff50cb" # m1.large
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}
resource "openstack_blockstorage_volume_v2" "aarnet-db" {
  name  = "aarnet-db-volume"
  size  = 1000
}
resource "openstack_compute_volume_attach_v2" "aarnet-db-attach" {
  instance_id = openstack_compute_instance_v2.aarnet-db.id
  volume_id = openstack_blockstorage_volume_v2.aarnet-db.id
}


# application server / web server
resource "openstack_compute_instance_v2" "aarnet-web" {
  name            = "aarnet-web"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "753fd5f7-1395-44aa-b3d8-1d33fa5a8823" # m1.xlarge
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "Web-Services", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}
resource "openstack_blockstorage_volume_v2" "aarnet-web" {
  name  = "aarnet-web-volume"
  size  = 1000
}
resource "openstack_compute_volume_attach_v2" "aarnet-web-attach" {
  instance_id = openstack_compute_instance_v2.aarnet-web.id
  volume_id = openstack_blockstorage_volume_v2.aarnet-web.id
}

# slurm / rabbitMQ
resource "openstack_compute_instance_v2" "aarnet-mq" {
  name            = "aarnet-mq"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "753fd5f7-1395-44aa-b3d8-1d33fa5a8823" # m1.xlarge
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "Web-Services", "rabbitmq", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}
resource "openstack_blockstorage_volume_v2" "aarnet-mq" {
  name  = "aarnet-mq-volume"
  size  = 1000
}
resource "openstack_compute_volume_attach_v2" "aarnet-mq-attach" {
  instance_id = openstack_compute_instance_v2.aarnet-mq.id
  volume_id = openstack_blockstorage_volume_v2.aarnet-mq.id
}

# slurm workers
resource "openstack_compute_instance_v2" "aarnet-worker-1" {
  name            = "aarnet-w1"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "753fd5f7-1395-44aa-b3d8-1d33fa5a8823" # m1.xlarge
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}
resource "openstack_blockstorage_volume_v2" "aarnet-worker-1" {
  name  = "aarnet-worker-1-volume"
  size  = 1000
}
resource "openstack_compute_volume_attach_v2" "aarnet-worker-1-attach" {
  instance_id = openstack_compute_instance_v2.aarnet-worker-1.id
  volume_id = openstack_blockstorage_volume_v2.aarnet-worker-1.id
}

resource "openstack_compute_instance_v2" "aarnet-worker-2" {
  name            = "aarnet-w2"
  image_id        = "47e4fca7-cae0-4d2e-9ec0-799d61f9604b" # ubuntu 20.04
  flavor_id       = "753fd5f7-1395-44aa-b3d8-1d33fa5a8823" # m1.xlarge
  key_pair        = "galaxy-dev-key"
  security_groups = ["SSH-ICMP", "default"]
  availability_zone = "nova"
  network {
    uuid = "520b0ec5-a3ff-4c02-bb37-988a554cc219" # ext-net
  }
  network {
    uuid = openstack_networking_network_v2.network.id # galaxy-int-net
  }
}
resource "openstack_blockstorage_volume_v2" "aarnet-worker-2" {
  name  = "aarnet-worker-2-volume"
  size  = 1000
}
resource "openstack_compute_volume_attach_v2" "aarnet-worker-2-attach" {
  instance_id = openstack_compute_instance_v2.aarnet-worker-2.id
  volume_id = openstack_blockstorage_volume_v2.aarnet-worker-2.id
}
