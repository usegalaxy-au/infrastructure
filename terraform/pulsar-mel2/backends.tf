terraform {
  backend "swift" {
    container         = "terraform-state-pulsar-mel2"
    archive_container = "terraform-state-pulsar-mel2-archive"
  }
}
