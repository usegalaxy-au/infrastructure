terraform {
  backend "swift" {
    container         = "terraform-state-pulsar-mel3"
    archive_container = "terraform-state-pulsar-mel3-archive"
  }
}
