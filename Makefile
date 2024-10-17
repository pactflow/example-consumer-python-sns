# Default to the read only token - the read/write token will be present on Travis CI.
# It's set as a secure environment variable in the .travis.yml file
PACTICIPANT := "pactflow-example-consumer-python-kafka"
GITHUB_WEBHOOK_UUID := "c76b601e-d66a-4eb1-88a4-6ebc50c0df8b"
PACT_CLI="docker run --rm -v ${PWD}:${PWD} -e PACT_BROKER_BASE_URL -e PACT_BROKER_TOKEN pactfoundation/pact-cli:latest"

# Only deploy from main
ifeq ($(GIT_BRANCH),main)
	DEPLOY_TARGET=deploy
else
	DEPLOY_TARGET=no_deploy
endif

all: test

## ====================
## CI tasks
## ====================

ci: test publish_pacts can_i_deploy $(DEPLOY_TARGET)

# Run the ci target from a developer machine with the environment variables
# set as if it was on Travis CI.
# Use this for quick feedback when playing around with your workflows.
fake_ci:
	CI=true \
	GIT_COMMIT=`git rev-parse --short HEAD`+`date +%s` \
	GIT_BRANCH=`git rev-parse --abbrev-ref HEAD` \
	make ci


publish_pacts:
	@"${PACT_CLI}" publish ${PWD}/pacts --consumer-app-version ${GIT_COMMIT} --tag ${GIT_BRANCH} --branch ${GIT_BRANCH} 

## =====================
## Build/test tasks
## =====================

test:
	python3 -m pytest

## =====================
## Deploy tasks
## =====================

create_environment:
	@"${PACT_CLI}" broker create-environment --name production --production

deploy: deploy_app record_deployment

no_deploy:
	@echo "Not deploying as not on main branch"

can_i_deploy:
	@"${PACT_CLI}" broker can-i-deploy \
	  --pacticipant ${PACTICIPANT} \
	  --version ${GIT_COMMIT} \
	  --to-environment production \
	  --retry-while-unknown 5 \
	  --retry-interval 10

deploy_app:
	@echo "Deploying to production"

record_deployment:
	@"${PACT_CLI}" broker record-deployment --pacticipant ${PACTICIPANT} --version ${GIT_COMMIT} --environment production

## =====================
## Pactflow set up tasks
## =====================

# This should be called once before creating the webhook
# with the environment variable GITHUB_TOKEN set
create_github_token_secret:
	@curl -v -X POST ${PACT_BROKER_BASE_URL}/secrets \
	-H "Authorization: Bearer ${PACT_BROKER_TOKEN}" \
	-H "Content-Type: application/json" \
	-H "Accept: application/hal+json" \
	-d  "{\"name\":\"githubCommitStatusToken\",\"description\":\"Github token for updating commit statuses\",\"value\":\"${GITHUB_TOKEN}\"}"

# This webhook will update the Github commit status for this commit
# so that any PRs will get a status that shows what the status of
# the pact is.
create_or_update_github_webhook:
	@"${PACT_CLI}" \
	  broker create-or-update-webhook \
	  'https://api.github.com/repos/pactflow/example-consumer-python-kafka/statuses/$${pactbroker.consumerVersionNumber}' \
	  --header 'Content-Type: application/json' 'Accept: application/vnd.github.v3+json' 'Authorization: token $${user.githubCommitStatusToken}' \
	  --request POST \
	  --data @${PWD}/pactflow/github-commit-status-webhook.json \
	  --uuid ${GITHUB_WEBHOOK_UUID} \
	  --consumer ${PACTICIPANT} \
	  --contract-published \
	  --provider-verification-published \
	  --description "Github commit status webhook for ${PACTICIPANT}"

test_github_webhook:
	@curl -v -X POST ${PACT_BROKER_BASE_URL}/webhooks/${GITHUB_WEBHOOK_UUID}/execute -H "Authorization: Bearer ${PACT_BROKER_TOKEN}"

## ======================
## Misc
## ======================

.PHONY: test

## ======================
## Python additions
## ======================
PROJECT := example-consumer-python-kafka
PYTHON_MAJOR_VERSION := 3.11

sgr0 := $(shell tput sgr0)
red := $(shell tput setaf 1)
green := $(shell tput setaf 2)

deps:
	poetry install

venv:
	@if [ -d "./.venv" ]; then echo "$(red).venv already exists, not continuing!$(sgr0)"; exit 1; fi
	@type pyenv >/dev/null 2>&1 || (echo "$(red)pyenv not found$(sgr0)"; exit 1)

	@echo "\n$(green)Try to find the most recent minor version of the major version specified$(sgr0)"
	$(eval PYENV_VERSION=$(shell pyenv install -l | grep "\s\s$(PYTHON_MAJOR_VERSION)\.*" | tail -1 | xargs))
	@echo "$(PYTHON_MAJOR_VERSION) -> $(PYENV_VERSION)"

	@echo "\n$(green)Install the Python pyenv version if not already available$(sgr0)"
	pyenv install $(PYENV_VERSION) -s

	@echo "\n$(green)Make a .venv dir$(sgr0)"
	~/.pyenv/versions/${PYENV_VERSION}/bin/python3 -m venv ${CURDIR}/.venv

	@echo "\n$(green)Make it 'available' to pyenv$(sgr0)"
	ln -sf ${CURDIR}/.venv ~/.pyenv/versions/${PROJECT}

	@echo "\n$(green)Use it! (populate .python-version)$(sgr0)"
	pyenv local ${PROJECT}

run:
	python3 run.py