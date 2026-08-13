variable "aws_region" {
  description = "AWS region for the prototype."
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 size used by the single-host prototype."
  type        = string
  default     = "t3.small"
}

variable "allowed_http_cidr" {
  description = "CIDR allowed to reach the public HTTP endpoint."
  type        = string
  default     = "0.0.0.0/0"
}

variable "project_name" {
  description = "Short resource-name prefix."
  type        = string
  default     = "pace-talent-pool"
}
