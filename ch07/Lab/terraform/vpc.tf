resource "aws_vpc" "this" {

  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_internet_gateway" "this" {

  vpc_id = aws_vpc.this.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_eip" "nat" {
  vpc = true

}

resource "aws_nat_gateway" "nat" {

  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.this.id
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_subnet" "this" {

  cidr_block              = "10.0.0.0/16"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.this.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route_table" "this" {

  vpc_id = aws_vpc.this.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route" "this" {

  route_table_id         = aws_route_table.this.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route_table_association" "this" {

  route_table_id = aws_route_table.this.id
  subnet_id      = aws_subnet.this.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "allow-ssh" {
  vpc_id      = aws_vpc.this.id
  name        = "allow-ssh"
  description = "security group that allows ssh and all egress traffic"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["224.0.0.0/24"]
  }


  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  ingress {
    from_port   = 8675
    to_port     = 8675
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  ingress {
    from_port   = 7443
    to_port     = 7443
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  tags = {
    Name = "allow-ssh"
  }
}

resource "aws_security_group" "ghh_windows" {
  vpc_id      = aws_vpc.this.id
  name        = "ghh_windows"
  description = "security group that allows windows ports"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["224.0.0.0/24"]
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  ingress {
    from_port   = 5985
    to_port     = 5986
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  tags = {
    Name = "ghh-rules"
  }
}

