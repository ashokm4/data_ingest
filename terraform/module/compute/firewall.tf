resource "google_compute_firewall" "rules" {
#  project     = "my-project-name"
  name        = "${var.name}-filewall-${var.machine_type}"
  network     = "default"
  description = "Creates firewall rule targeting tagged instances"

    allow {
    protocol  = "tcp"
    ports     =  var.ports
  }
  source_ranges = ["192.168.86.31/32"]
  target_tags = ["foo"]
}
