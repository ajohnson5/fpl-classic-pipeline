locals {
  default = tomap({ for tuple in regexall("(.*)=(.*)", file("../.env")) : tuple[0] => tuple[1] })
}

data "template_file" "startup_script" {
  template = file("./start_up/start_up_script.sh")
  vars = {
    PROJECT_ID = local.default.PROJECT_ID
    PROJECT_DATASET = local.default.PROJECT_DATASET
    PROJECT_BUCKET = local.default.PROJECT_BUCKET
    LEAGUE_ID = local.default.LEAGUE_ID
    POSTGRES_USERNAME = local.default.POSTGRES_USERNAME
    POSTGRES_PASSWORD = local.default.POSTGRES_PASSWORD
    POSTGRES_DB = local.default.POSTGRES_DB
  }
}

provider "google" { 
  project = local.default.PROJECT_ID
  region = "europe-west2"
  zone = "europe-west2-c"
}


resource "google_service_account" "default" {
  account_id   = "fpl-service-account"
  display_name = "fpl_service_account"
}


resource "google_project_iam_member" "member-role" {
  for_each = toset([
    "roles/storage.admin",
    "roles/bigquery.admin"
  ])
  role = each.key
  member = "serviceAccount:${google_service_account.default.email}"
  project = local.default.PROJECT_ID
}


resource "google_storage_bucket" "static" {
 name          = local.default.PROJECT_BUCKET
 location      = "EUROPE-WEST2"
 storage_class = "STANDARD"
 uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = local.default.PROJECT_DATASET
  location = "EU"
  project = local.default.PROJECT_ID
}


resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}

resource "google_compute_firewall" "ssh-rule" { 
  name = "ssh-res"
  network = google_compute_network.vpc_network.name
  allow {
    protocol = "tcp"
    ports = ["22"]
  }
  target_tags = ["fpl-pipeline-test"]
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "vm_instance" {
  name = "fpl-pipeline-test"
  tags = ["fpl-pipeline-test"]
  machine_type = "e2-standard-2"
  zone = "europe-west2-c"
  boot_disk {
    initialize_params {
    image = "ubuntu-2004-focal-v20230302"
    size = 30
    }
  }

network_interface {
  network = google_compute_network.vpc_network.name
  access_config {
  }
}

metadata_startup_script= data.template_file.startup_script.rendered

service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.default.email
    scopes = ["bigquery","storage-full"]
  }
}