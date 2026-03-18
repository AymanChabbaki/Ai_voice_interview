output "master_public_ip" {
  description = "Public IP of the K3s master node"
  value       = aws_instance.master.public_ip
}

output "worker_public_ip" {
  description = "Public IP of the K3s worker node"
  value       = aws_instance.worker.public_ip
}

output "ssh_master_command" {
  description = "Quick SSH command for the master node"
  value       = "ssh ubuntu@${aws_instance.master.public_ip}"
}

output "ssh_worker_command" {
  description = "Quick SSH command for the worker node"
  value       = "ssh ubuntu@${aws_instance.worker.public_ip}"
}
