terraform {
  backend "swift" {
    container         = "terraform-state-pawsey"
    archive_container = "terraform-state-pawsey-archive"
  }
}
