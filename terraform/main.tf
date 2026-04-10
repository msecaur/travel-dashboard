provider "aws" {
  region = "us-east-2"
}

resource "aws_security_group" "travel_dashboard_sg" {
  name        = "travel-dashboard-sg"
  description = "Security group for travel dashboard"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "travel_dashboard" {
  ami           = "ami-0862be96e41dcbf74"
  instance_type = "t2.micro"
  key_name      = "Travel-Dashboard-ec2-part3"

  vpc_security_group_ids = [aws_security_group.travel_dashboard_sg.id]

  tags = {
    Name = "travel-dashboard"
  }
}

output "public_ip" {
  value = aws_instance.travel_dashboard.public_ip
}

output "public_dns" {
  value = aws_instance.travel_dashboard.public_dns
}
