resource "google_compute_address" "external-ip" {
  name = "external-ipv4-address-${var.name}"
}


resource "google_compute_instance" "default" {
  name         = var.name
  machine_type = var.machine_type
#  zone         = var.zone
  tags =  var.tags

  boot_disk {
    initialize_params {
      image = var.image
    }
  }

  // Local SSD disk
#  scratch_disk {
#    interface = "SCSI"
#  }

network_interface {
network = "default"
access_config {
  nat_ip = google_compute_address.external-ip.address
}
}


  metadata = var.metadata
}
