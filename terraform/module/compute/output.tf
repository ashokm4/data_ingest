output instance_private_ip {
    value =  google_compute_instance.default.network_interface.0.network_ip
}

output instance_public_ip {
    value =  google_compute_address.external-ip.address
}
