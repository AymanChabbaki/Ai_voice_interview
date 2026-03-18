variable "project_name" {
  description = "Project prefix used for resource names/tags"
  type        = string
  default     = "smart-interviewer"
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Existing AWS EC2 Key Pair name for SSH access"
  type        = string
  default     = ""
}

variable "public_key_path" {
  description = "Path to local SSH public key (.pub). Used when key_name is empty."
  type        = string
  default     = ""
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into nodes"
  type        = string
  default     = "0.0.0.0/0"
}
