GIT_HASH := v$(shell git rev-parse --short HEAD)

develop:
	docker-compose -f .development/docker-compose.yml up -d 

develop-logs:
	docker-compose -f .development/docker-compose.yml logs -f

clean:
	docker-compose -f .development/docker-compose.yml down

docker-login:
	@eval "$(shell aws ecr get-login --region $(AWS_DEFAULT_REGION) --no-include-email)"

build: docker-login
	docker build -t vmi:latest -f .docker/Dockerfile .
	docker tag vmi "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com/vmi:$(GIT_HASH)"
	docker push "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com/vmi:$(GIT_HASH)"
	.deployment/Dockerrun.aws.json.sh | aws s3 cp - s3://vmi.$(ENVIRONMENT).bucket/$(GIT_HASH)/Dockerrun.aws.json
	aws elasticbeanstalk create-application-version --application-name accio_alert-dev --version-label $(GIT_HASH) --description "Version created from gitlab ci" --source-bundle S3Bucket="vmi.$(ENVIRONMENT).bucket",S3Key="$(GIT_HAHS)/Dockerrun.aws.json"

deploy:
	aws elasticbeanstalk update-environment --environment-name vmi-$(ENVIRONMENT)-env --version-label $(GIT_HASH)

init:
	.deployment/terraform init .deployment/

plan: init
	.deployment/terraform plan -var 'environment=$(ENVIRONMENT)' -var 'version=$(GIT_HASH)' -var 'db_username=$(DB_USER)' .deployment/

infrastructure: plan
	.deployment/terraform apply -auto-approve -var 'environment=$(ENVIRONMENT)' -var 'version=$(GIT_HASH)' -var 'db_username=$(DB_USER)' .deployment/
	
