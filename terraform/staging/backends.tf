terraform {
  backend "swift" {
    container         = "terraform-state-staging"
    archive_container = "terraform-state-staging-archive"
  }
}
