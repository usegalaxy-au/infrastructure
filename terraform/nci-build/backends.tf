terraform {
  backend "swift" {
    container         = "terraform-state-nci-build"
  }
}
