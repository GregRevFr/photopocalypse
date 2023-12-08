# Run the FastAPI server
run-api:
	@echo "Starting FastAPI server..."
	uvicorn photopocalypse.api.fast:app --host 0.0.0.0 --port 8080 --reload

# Variables
GCP_REGION := europe-west1
REPO_NAME := phurge
GCP_PROJECT := bootcamp-23
IMAGE_NAME := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(REPO_NAME)/$(REPO_NAME)
MEMORY_SIZE := 8Gi

.PHONY: build-prod build-intel tag-intel push-intel deploy

# Build production image
build-prod:
	docker build -t $(IMAGE_NAME):prod .

# Build Intel image
build-intel:
	docker build --platform linux/amd64 -t $(REPO_NAME):intel .

# Tag Intel image
tag-intel: build-intel
	docker tag $(REPO_NAME):intel $(IMAGE_NAME):intel

# Push Intel image to GCP
push-intel: tag-intel
	docker push $(IMAGE_NAME):intel

# Deploy to Google Cloud Run
deploy: push-intel
	gcloud run deploy --image $(IMAGE_NAME):intel --memory $(MEMORY_SIZE) --region $(GCP_REGION)
