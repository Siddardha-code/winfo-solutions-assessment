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
  default     = "1.32"
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
