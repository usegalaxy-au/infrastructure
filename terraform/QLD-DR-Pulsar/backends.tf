terraform {
  backend "swift" {
    container         = "terraform-state"
    archive_container = "terraform-state-archive"
  }
}
