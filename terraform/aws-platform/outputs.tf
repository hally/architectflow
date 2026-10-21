output "load_balancer_url" {
  description = "HTTP-only demonstration endpoint. Add HTTPS before real usage."
  value       = "http://${aws_lb.web.dns_name}"
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.app.name
}

output "efs_file_system_id" {
  value = aws_efs_file_system.data.id
}
