provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Application = "PACE Fresher Talent Pool"
      Environment = "prototype"
      ManagedBy   = "Terraform"
    }
  }
}
