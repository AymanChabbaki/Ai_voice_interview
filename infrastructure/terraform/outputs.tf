output "resource_group" {
  value = azurerm_resource_group.this.name
}

output "master_public_ip" {
  value = azurerm_public_ip.master.ip_address
}

output "master_private_ip" {
  value = azurerm_network_interface.master.private_ip_address
}

output "worker_private_ips" {
  value = {
    for name, nic in azurerm_network_interface.workers :
    name => nic.private_ip_address
  }
}

output "ssh_to_master" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.master.ip_address}"
}
