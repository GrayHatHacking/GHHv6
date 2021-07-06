resource "aws_route53_zone" "private" {
  name = var.dns_zone

  vpc {
    vpc_id = aws_vpc.this.id
  }
}