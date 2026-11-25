output "ecr_repository_url" { value = aws_ecr_repository.app.repository_url }
output "github_deployer_role_arn" { value = aws_iam_role.github_deployer.arn }
output "app_role_arn" { value = module.app_irsa.iam_role_arn }
output "cluster_name" { value = module.eks.cluster_name }
output "kubeconfig_command" { value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}" }
