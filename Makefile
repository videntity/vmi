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

init:
	.deployment/terraform init .deployment/

plan: init
	.deployment/terraform plan -var 'environment=$(ENVIRONMENT)' -var 'version=$(GIT_HASH)' -var 'db_username=$(DB_USER)' .deployment/

deploy: plan
	.deployment/terraform apply -auto-approve -var 'environment=$(ENVIRONMENT)' -var 'version=$(GIT_HASH)' -var 'db_username=$(DB_USER)' .deployment/
	
