import whisper
from fastapi import FastAPI


def initialize_variable(app: FastAPI):
    # Initialize your variable here
    model = whisper.load_model("base")
    app.model = model  # Assign the variable to the FastAPI app


def startup_event_handler():
    def startup_handler():
        initialize_variable(
            FastAPI
        )  # Call the initialization function during the startup event

    return startup_handler
