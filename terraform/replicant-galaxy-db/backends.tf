terraform {
  backend "swift" {
    container         = "terraform-state-galaxy-replicant-db"
    archive_container = "terraform-state-galaxy-replicant-db-archive"
  }
}
