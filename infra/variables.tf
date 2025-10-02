variable "env" {
  type        = string
  description = "Environment of current provision."
  default     = "local"
}

variable "aws_region" {
  type = string
  description = "Region for AWS services to be provisioned in."
  default = "eu-west-2"
}