
#variable instance_no {
#  type  = number
#}

variable name {
  type  = string
}

variable prvd {
  type  = string
  default = "google"
}

variable machine_type {
  type  = string
  default = "e2-micro"
}

variable tags {
  type  = list(string)
  default =  ["foo", "bar"]
}

variable ports {
  type = list(number)
  default = [80, 8080, 22]
}

variable image {
  type  = string
  default = "debian-cloud/debian-11"
}

variable network {
  type  = string
 default = "default"
}

variable zone {
  type  = string
}

variable metadata {
  type  =  map
  default = { foo = "bar"}
}
