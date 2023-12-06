## Run the FastAPI server
run-api:
	@echo "Starting FastAPI server..."
	uvicorn photopocalypse.api.fast:app --host 0.0.0.0 --port 8080 --reload
