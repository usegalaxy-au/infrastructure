terraform {
  backend "swift" {
    container         = "terraform-state-qld-himem"
    archive_container = "terraform-state-qld-himem-archive"
  }
}
