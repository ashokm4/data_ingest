locals {
  account_owner = 
  zone          = "us-central1-a"
  project       = 
  services = [
    "compute.googleapis.com",
  ]
}
terraform {
  backend "gcs" {
  bucket =  
  prefix   = "dev"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.39.0"
    }
  }
}



provider "google" {
  project = local.project
  region  = "us-central1"
  zone    = "us-central1-a"
}




resource "google_project_service" "enable_apis" {
  for_each = toset(local.services)
  #  project  = local.project
  project = local.project
  service = each.key
  timeouts {
    create = "30m"
    update = "40m"
  }
}




module "data_ingest" {
  source      = "../module/compute"
  name        = "data-ingest"
  zone        = local.zone
  machine_type = "e2-standard-4"
  metadata = {
    "ssh-keys" = 
  }
}
output "instance_private_ip" {
  value = module.data_ingest.instance_private_ip
}
output "instance_public_ip" {
  value = module.data_ingest.instance_public_ip
}
