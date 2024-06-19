# NOTE: don't need to create this key as it is already defined in the tenancy
/*
resource "openstack_compute_keypair_v2" "galaxy-australia" {
  name       = "galaxy-australia"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8TymxWTJSmirXaZKdFebz2vRpKWQD881XpqceMEpTJ/i46sR4rRwFOlYR19Zpr8dyMjkZ/hxWGVG60vKKFKcqzoTJ/aTbfSF4FUyVlb84XEig+9w1LZ7kTmrX4qRQZIuf6b21FOOaLrF+xcGSnbidQ8aKzEAFv1jxWHV7jTE/Np/ne2Ir2CdH7Qq9bz680mArBK/L056GY+4rwUNINW2YiZT+5qP3nOKHW7JYXovOdZyZIAKUmb8/O7EK6GxPyUh5DkkL1z9tcgQ/ZB0XM9h4igcvPJkRyqXpN1Tdm36aByF2gkXxpdpSLYsMKMHcYGE4zVanhKCi1ucenWFn0t/z Generated-by-Nova"
}
*/

# openstack_compute_instance_v2.pulsar-qld-gpu1:
resource "openstack_compute_instance_v2" "pulsar-qld-gpu1" {
  name              = "pulsar-qld-gpu1"
  image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

# openstack_compute_instance_v2.pulsar-qld-gpu2:
resource "openstack_compute_instance_v2" "pulsar-qld-gpu2" {
  name              = "pulsar-qld-gpu2"
  image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

# openstack_compute_instance_v2.pulsar-qld-gpu3:
resource "openstack_compute_instance_v2" "pulsar-qld-gpu3" {
  name              = "pulsar-qld-gpu3"
  image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

# openstack_compute_instance_v2.pulsar-qld-gpu4:
resource "openstack_compute_instance_v2" "pulsar-qld-gpu4" {
  name              = "pulsar-qld-gpu4"
  image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

# openstack_compute_instance_v2.gpu-test-clean:
resource "openstack_compute_instance_v2" "gpu-test-clean" {
  name              = "gpu-test-clean"
  image_id          = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

# openstack_compute_instance_v2.gpu-tool-test:
resource "openstack_compute_instance_v2" "gpu-tool-test" {
  name              = "gpu-tool-test"
  flavor_name       = "qld.64c600g.A100.nvme"
  key_pair          = "galaxy-australia"
  block_device {
    uuid                  = "d3fd2c57-d3a3-4c4f-84b6-e20d367431e7" # NeCTAR Ubuntu 22.04 LTS (Jammy) amd64
    source_type           = "image"
    volume_size           = 240
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }
  security_groups   = [
      "default",
      "SSH only"
  ]
  availability_zone = "QRIScloud"
}

