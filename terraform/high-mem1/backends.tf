terraform {
  backend "swift" {
    container         = "terraform-state-high-mem1"
    archive_container = "terraform-state-high-mem1-archive"
  }
}
