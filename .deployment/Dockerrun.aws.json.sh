#!/bin/bash

cat << EOF
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "567024208163.dkr.ecr.us-east-1.amazonaws.com/vmi:$1",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "80"
    }
  ],
  "Logging": "/var/log/nginx"
}
EOF
