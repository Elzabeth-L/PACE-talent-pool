output "instance_id" {
  value = aws_instance.app.id
}

output "public_ip" {
  value = aws_instance.app.public_ip
}

output "application_url" {
  value = "http://${aws_instance.app.public_ip}"
}

output "application_dns_url" {
  value = "http://${aws_instance.app.public_dns}"
}

output "deployment_bucket" {
  value = aws_s3_bucket.deployment.id
}
