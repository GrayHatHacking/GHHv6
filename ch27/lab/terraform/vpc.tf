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
