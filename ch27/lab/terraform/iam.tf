#IAM Role
resource "aws_iam_role" "ghh-ec2-role" {
  name = "ghh-ec2-role-${random_string.random.id}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
  tags = {
      Name = "ghh-ec2-role-${random_string.random.id}"
  }
}

#Iam Role Policy
resource "aws_iam_policy" "ghh-ec2-role-policy" {
  name = "ghh-ec2-role-policy-${random_string.random.id}"
  description = "ghh-ec2-role-policy-${random_string.random.id}"
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::ghh-s3-bucket-${random_string.random.id}/*",
                "arn:aws:s3:::ghh-s3-bucket-${random_string.random.id}",
                "arn:aws:s3:::ghh-sam-bucket-${random_string.random.id}/*",
                "arn:aws:s3:::ghh-sam-bucket-${random_string.random.id}"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "cloudwatch:*",
                "ec2:*",
                "cloudformation:*",
                "iam:*",
                "ssm:*",
                "events:*"
            ],
            "Resource": "*"
        }
    ]
}
POLICY
}

#IAM Role Policy Attachment
resource "aws_iam_policy_attachment" "ghh-ec2-role-policy-attachment" {
  name = "ghh-ec2-role-policy-attachment-${random_string.random.id}"
  roles = [aws_iam_role.ghh-ec2-role.name]
  policy_arn = aws_iam_policy.ghh-ec2-role-policy.arn
}
#IAM Instance Profile
resource "aws_iam_instance_profile" "ghh-ec2-instance-profile" {
  name = "ghh-ec2-instance-profile-${random_string.random.id}"
  role = aws_iam_role.ghh-ec2-role.name
}
