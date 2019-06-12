provider "aws" {}

terraform {
  backend "s3" {
    bucket  = "videntity.terraform-state-dev"
    key     = "vmi/terraform.tfstate"
    encrypt = true
  }
}

##############################################################
# Data sources to get VPC, subnets and security group details
##############################################################
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "all" {
  vpc_id = "${data.aws_vpc.default.id}"
}

data "aws_security_group" "default" {
  vpc_id = "${data.aws_vpc.default.id}"
  name   = "default"
}

# sec group
resource "aws_security_group" "vmi" {
  vpc_id      = "${data.aws_vpc.default.id}"
  name        = "vmi-${var.environment}"
  description = "App ${var.environment} security group"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    environment = "${var.environment}"
  }
}

resource "aws_security_group_rule" "allow-postgres" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = "${data.aws_security_group.default.id}"
  source_security_group_id = "${aws_security_group.vmi.id}"
}

variable "environment" {
  type = "string"
}

variable "dbname" {
  type    = "string"
  default = "devdb"
}

variable "db_size" {
  type    = "string"
  default = "db.t2.micro"
}

variable "db_username" {
  type = "string"
}

resource "random_string" "db_password" {
  length  = 16
  special = false
}

#####
# DB
#####
module "db" {
  source = "terraform-aws-modules/rds/aws"
  version = "1.28.0"
  identifier = "${var.dbname}"

  engine            = "postgres"
  engine_version    = "9.6.11"
  instance_class    = "${var.db_size}"
  allocated_storage = 5
  storage_encrypted = false

  # kms_key_id        = "arm:aws:kms:<region>:<account id>:key/<kms key id>"

  # NOTE: Do NOT use 'user' as the value for 'username' as it throws:
  # "Error creating DB Instance: InvalidParameterValue: MasterUsername
  # user cannot be used as it is a reserved word used by the engine"
  username = "${var.db_username}"
  password               = "${random_string.db_password.result}"
  port                   = "5432"
  name                   = "vmi"
  vpc_security_group_ids = ["${data.aws_security_group.default.id}"]
  maintenance_window     = "Mon:00:00-Mon:03:00"
  backup_window          = "03:00-06:00"
  # disable backups to create DB faster
  backup_retention_period = 0
  tags = {
    environment = "${var.environment}"
  }
  # DB subnet group
  subnet_ids = ["${data.aws_subnet_ids.all.ids}"]
  # DB parameter group
  family = "postgres9.6"
  # DB option group
  major_engine_version = "9.6"
  # Snapshot name upon DB deletion
  final_snapshot_identifier = "${var.dbname}"
}

resource "aws_ssm_parameter" "db_uri" {
  name        = "/${var.environment}/vmi/database/DATABASES_CUSTOM"
  description = "Database uri"
  type        = "SecureString"
  value       = "postgres://${var.db_username}:${random_string.db_password.result}@${module.db.this_db_instance_endpoint}/vmi"

  tags {
    environment = "${var.environment}"
  }
}

resource "aws_s3_bucket" "default" {
  bucket = "vmi.${var.environment}.bucket"
  acl    = "private"

  tags {
    environment = "${var.environment}"
  }
}

resource "aws_ecr_repository" "vmi" {
  name = "vmi"
}

#
# EC2
#
data "aws_iam_policy_document" "ec2" {
  statement {
    sid = ""

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    effect = "Allow"
  }

  statement {
    sid = ""

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    effect = "Allow"
  }
}

resource "aws_iam_role" "ec2" {
  name               = "vmi-eb-ec2"
  assume_role_policy = "${data.aws_iam_policy_document.ec2.json}"
}

resource "aws_iam_role_policy" "default" {
  name   = "vmi-eb-default"
  role   = "${aws_iam_role.ec2.id}"
  policy = "${data.aws_iam_policy_document.default.json}"
}

resource "aws_iam_role_policy_attachment" "web-tier" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy_attachment" "worker-tier" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
}

resource "aws_iam_role_policy_attachment" "ssm-ec2" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "ssm-automation" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole"

  lifecycle {
    create_before_destroy = true
  }
}

# http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker.container.console.html
# http://docs.aws.amazon.com/AmazonECR/latest/userguide/ecr_managed_policies.html#AmazonEC2ContainerRegistryReadOnly
resource "aws_iam_role_policy_attachment" "ecr-readonly" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ssm-readonly" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "ses-all" {
  role       = "${aws_iam_role.ec2.name}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

data "aws_iam_policy_document" "default" {
  statement {
    sid = ""

    actions = [
      "elasticloadbalancing:DescribeInstanceHealth",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeTargetHealth",
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:GetConsoleOutput",
      "ec2:AssociateAddress",
      "ec2:DescribeAddresses",
      "ec2:DescribeSecurityGroups",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeScalingActivities",
      "autoscaling:DescribeNotificationConfigurations",
    ]

    resources = ["*"]

    effect = "Allow"
  }

  statement {
    sid = "AllowOperations"

    actions = [
      "autoscaling:AttachInstances",
      "autoscaling:CreateAutoScalingGroup",
      "autoscaling:CreateLaunchConfiguration",
      "autoscaling:DeleteLaunchConfiguration",
      "autoscaling:DeleteAutoScalingGroup",
      "autoscaling:DeleteScheduledAction",
      "autoscaling:DescribeAccountLimits",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeLoadBalancers",
      "autoscaling:DescribeNotificationConfigurations",
      "autoscaling:DescribeScalingActivities",
      "autoscaling:DescribeScheduledActions",
      "autoscaling:DetachInstances",
      "autoscaling:PutScheduledUpdateGroupAction",
      "autoscaling:ResumeProcesses",
      "autoscaling:SetDesiredCapacity",
      "autoscaling:SuspendProcesses",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "autoscaling:UpdateAutoScalingGroup",
      "cloudwatch:PutMetricAlarm",
      "ec2:AssociateAddress",
      "ec2:AllocateAddress",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:DescribeAccountAttributes",
      "ec2:DescribeAddresses",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSnapshots",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:DisassociateAddress",
      "ec2:ReleaseAddress",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:TerminateInstances",
      "ecs:CreateCluster",
      "ecs:DeleteCluster",
      "ecs:DescribeClusters",
      "ecs:RegisterTaskDefinition",
      "elasticbeanstalk:*",
      "elasticloadbalancing:ApplySecurityGroupsToLoadBalancer",
      "elasticloadbalancing:ConfigureHealthCheck",
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
      "elasticloadbalancing:DescribeInstanceHealth",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeTargetHealth",
      "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:RegisterTargets",
      "elasticloadbalancing:DeregisterTargets",
      "iam:ListRoles",
      "iam:PassRole",
      "logs:CreateLogGroup",
      "logs:PutRetentionPolicy",
      "rds:DescribeDBEngineVersions",
      "rds:DescribeDBInstances",
      "rds:DescribeOrderableDBInstanceOptions",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:ListBucket",
			"s3:PutObject",
      "s3:DeleteObject",
      "s3:PutObjectAcl",
      "sns:CreateTopic",
      "sns:GetTopicAttributes",
      "sns:ListSubscriptionsByTopic",
      "sns:Subscribe",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "codebuild:CreateProject",
      "codebuild:DeleteProject",
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
    ]

    resources = ["*"]

    effect = "Allow"
  }

  statement {
    sid = "AllowS3OperationsOnElasticBeanstalkBuckets"

    actions = [
      "s3:*",
    ]

    resources = [
      "arn:aws:s3:::*",
    ]

    effect = "Allow"
  }

  statement {
    sid = "AllowDeleteCloudwatchLogGroups"

    actions = [
      "logs:DeleteLogGroup",
    ]

    resources = [
      "arn:aws:logs:*:*:log-group:/aws/elasticbeanstalk*",
    ]

    effect = "Allow"
  }

  statement {
    sid = "AllowCloudformationOperationsOnElasticBeanstalkStacks"

    actions = [
      "cloudformation:*",
    ]

    resources = [
      "arn:aws:cloudformation:*:*:stack/awseb-*",
      "arn:aws:cloudformation:*:*:stack/eb-*",
    ]

    effect = "Allow"
  }
}

resource "aws_iam_instance_profile" "ec2" {
  name = "vmi-eb-ec2"
  role = "${aws_iam_role.ec2.name}"
}

resource "aws_elastic_beanstalk_application" "default" {
  name        = "vmi-${var.environment}"
  description = "vmi-${var.environment}-desc"
}

resource "aws_elastic_beanstalk_environment" "default" {
  name                = "vmi-${var.environment}-env"
  application         = "${aws_elastic_beanstalk_application.default.name}"
  solution_stack_name = "64bit Amazon Linux 2018.03 v2.12.3 running Docker 18.06.1-ce"

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = "${data.aws_vpc.default.id}"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = "${element(data.aws_subnet_ids.all.ids, 0)}"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "${aws_iam_instance_profile.ec2.name}"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = "${aws_security_group.vmi.id}"
  }
}

resource "aws_ssm_parameter" "allowed_host" {
  name        = "/${var.environment}/vmi/eb/ALLOWED_HOSTS"
  description = "Server hostname"
  type        = "SecureString"
  value       = "alpha.verifymyidentity.com"

  tags {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "oidc_issuer" {
  name        = "/${var.environment}/vmi/eb/OIDC_ISSUER"
  description = "Server hostname"
  type        = "SecureString"
  value       = "https://alpha.verifymyidentity.com"

  tags {
    environment = "${var.environment}"
  }
}
