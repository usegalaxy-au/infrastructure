terraform {
  backend "swift" {
    container         = "terraform-state-pulsar-qld-high-mem"
    archive_container = "terraform-state-pulsar-qld-high-mem-archive"
  }
}
