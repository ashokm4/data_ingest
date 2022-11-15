locals {
  account_owner = "ashok.mahajan@bigcommerce.com"
  zone          = "us-central1-a"
  project       = "dynamic-364900"
  services = [
    "compute.googleapis.com",
  ]
}
terraform {
  backend "gcs" {
  bucket =  "tfstat-carol-4256"
  prefix   = "dev"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.39.0"
    }
    daku = {
      source = "kreuzwerker/docker"
    }
  }
}



provider "google" {
  project = local.project
  region  = "us-central1"
  zone    = "us-central1-a"
}


#provider "golmol" {
#  project = "ashok-bc-test"
#  region  = "us-east1"
#  zone    = "us-east1-a"
#  alias   = "two"
#}


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
    "ssh-keys" = "${file("/Users/ashok.mahajan/personal/id_ed25519.pub")}"
  }
}
output "instance_private_ip" {
  value = module.data_ingest.instance_private_ip
}
output "instance_public_ip" {
  value = module.data_ingest.instance_public_ip
}
