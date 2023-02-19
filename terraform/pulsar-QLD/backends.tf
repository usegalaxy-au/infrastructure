terraform {
  backend "swift" {
    container         = "terraform-state-pulsar-QLD"
    archive_container = "terraform-state-pulsar-QLD-archive"
  }
}
