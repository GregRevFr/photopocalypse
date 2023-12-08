## Run the FastAPI server
run-api:
	@echo "Starting FastAPI server..."
	uvicorn photopocalypse.api.fast:app --host 0.0.0.0 --port 8080 --reload

# Defining variables for convenience
IMAGE_NAME=phurge-image-try
INTEL_IMAGE_TAG=$(IMAGE_NAME):intel
PROD_IMAGE_TAG=$(IMAGE_NAME):prod

# Default target
all: build-prod build-intel tag push deploy

# Default target
all-intel: build-intel tag push deploy

# Build the production Docker image
build-prod:
	docker build -t $(PROD_IMAGE_TAG) .

# Build the Intel architecture Docker image
build-intel:
	docker build --platform linux/amd64 -t phurge:intel .

# Tag the Intel image
tag:
	docker tag phurge:intel $(INTEL_IMAGE_TAG)

# Push the Intel image to the registry
push:
	docker push $(INTEL_IMAGE_TAG)

# Deploy the Intel image using gcloud
deploy:
	gcloud run deploy --image $(INTEL_IMAGE_TAG) --memory 8Gi --region europe-west1

# Helper target to clean up local images
clean:
	docker rmi $(PROD_IMAGE_TAG) phurge:intel $(INTEL_IMAGE_TAG)
