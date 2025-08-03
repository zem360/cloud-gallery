terraform {
  backend "s3" {
    bucket = "cloud-gallery-terraform-state-1754200541"
    key    = "cloud-gallery/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}