variable "region" {
  type    = string
  default = "us-east-1"
}
variable "cluster_name" {
  type    = string
  default = "ticket-assistant"
}
variable "kubernetes_version" {
  type        = string
  default     = "1.36"
  description = "Check the currently supported EKS versions before applying."
}
variable "github_repo" {
  type        = string
  description = "owner/repo allowed to deploy via GitHub OIDC"
}
variable "create_github_oidc_provider" {
  type        = bool
  default     = true
  description = "Set false if the account already has the token.actions.githubusercontent.com OIDC provider."
}
variable "namespace" {
  type    = string
  default = "support"
}
variable "github_owner_id" {
  description = "Numeric ID of the GitHub account that owns the repo"
  type        = string
  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "Use the numeric ID, for example 85091100."
  }
}

variable "github_repo_id" {
  description = "Numeric ID of the GitHub repository"
  type        = string
  validation {
    condition     = can(regex("^[0-9]+$", var.github_repo_id))
    error_message = "Use the numeric ID, for example 1471779706."
  }
}