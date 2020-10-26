terraform {
  backend "swift" {
    container         = "terraform-state-prod"
    archive_container = "terraform-state-prod-archive"
  }
}
