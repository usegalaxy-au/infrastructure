terraform {
  backend "swift" {
    container         = "terraform-state-qld-dr"
    archive_container = "terraform-state-qld-dr-archive"
  }
}
