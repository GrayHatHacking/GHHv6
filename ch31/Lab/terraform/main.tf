provider "aws" {
  shared_credentials_file = var.shared_credentials_file
  region                  = "us-east-1"
  profile                 = "ghh"
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  token                  = data.aws_eks_cluster_auth.cluster.token
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
}