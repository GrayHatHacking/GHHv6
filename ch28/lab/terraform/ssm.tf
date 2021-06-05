resource "aws_ssm_document" "perform_healthcheck" {
  name            = "PerformHealthcheck"
  document_type   = "Command"
  document_format = "YAML"

  content = file("documents/perform_healthcheck.yml")
}
