locals {
  kosli_src_path = "${path.module}/builds/kosli_${var.kosli_cli_version}"
}

resource "null_resource" "download_and_unzip" {
  triggers = {
    downloaded = "${local.kosli_src_path}/kosli.tar.gz"
  }

  provisioner "local-exec" {
    command = <<EOT
      mkdir -p ${local.kosli_src_path}/
      curl -Lo ${local.kosli_src_path}/kosli.tar.gz https://github.com/kosli-dev/cli/releases/download/v${var.kosli_cli_version}/kosli_${var.kosli_cli_version}_linux_amd64.tar.gz
      tar -xf ${local.kosli_src_path}/kosli.tar.gz -C ${local.kosli_src_path}/
    EOT
  }
}