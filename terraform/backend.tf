terraform {
  backend "s3" {
    # Backend configuration provided via backend-config.hcl or terraform init parameters
    # bucket  = provided via config
    # key     = "cloud-gallery/terraform.tfstate"
    # region  = "us-east-1"
    # encrypt = true
  }
}
