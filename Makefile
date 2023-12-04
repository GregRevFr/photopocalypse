## Run the FastAPI server
run-api:
	@echo "Starting FastAPI server..."
	uvicorn api.fast:app --host 0.0.0.0 --port 8000 --reload
