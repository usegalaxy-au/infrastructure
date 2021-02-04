terraform {
  backend "swift" {
    container         = "terraform-state-pulsar-nci-test"
  }
}
