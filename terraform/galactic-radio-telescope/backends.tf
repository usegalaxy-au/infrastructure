terraform {
  backend "swift" {
    container         = "terraform-state-grt"
    archive_container = "terraform-state-grt-archive"
  }
}
