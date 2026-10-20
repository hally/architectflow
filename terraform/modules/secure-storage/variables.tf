variable "bucket_name" {
  description = "Globally unique name for the private document bucket."
  type        = string
}

variable "project" {
  description = "Project ownership tag."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "owner" {
  description = "Business or technical owner."
  type        = string
}

variable "cost_center" {
  description = "Cost allocation identifier."
  type        = string
}
