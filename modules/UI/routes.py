from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Any, Dict

import yaml
import os

from modules.config_tools.config_validator import ConfigValidator

# Initialize the FastAPI app
app = FastAPI()

# Serve the static files (JS, CSS, images)
app.mount("/static", StaticFiles(directory="modules/UI/static"), name="static")

# Set up the templates directory for rendering HTML
templates = Jinja2Templates(directory="modules/UI/templates")

# Route to serve the main menu
@app.get("/main_menu")
async def main_menu(request: Request):
    return templates.TemplateResponse("main_menu.html", {"request": request})

# Function to load configuration rules from the YAML file
def load_config_rules():
    config_rules_path = os.path.join("configs", "validation", "config_rules.yaml")
    with open(config_rules_path, "r") as file:
        return yaml.safe_load(file)

# Route to serve the config rules as JSON
@app.get("/config_rules")
async def get_config_rules(request: Request):
    config_rules = load_config_rules()  # Load the config rules from YAML
    return JSONResponse(content=config_rules)

# Route to create a new configuration
@app.get("/new_config")
async def new_config(request: Request):
    config_rules = load_config_rules()  # Load the config rules
    return templates.TemplateResponse("new_config.html", {"request": request})

@app.get("/auth_files")
async def get_auth_files():
    auth_dir = os.path.join(os.getcwd(), "auth")
    try:
        # List all files in the /auth directory
        files = [f for f in os.listdir(auth_dir) if os.path.isfile(os.path.join(auth_dir, f))]
        return JSONResponse(content=files)
    except FileNotFoundError:
        return JSONResponse(content=[], status_code=404)

# Route to edit an existing configuration
@app.get("/edit_config")
async def edit_config(request: Request):
    return templates.TemplateResponse("edit_config.html", {"request": request})

# Route to view configurations
@app.get("/view_configs")
async def view_configs(request: Request):
    return templates.TemplateResponse("view_configs.html", {"request": request})

# Route to execute a configuration
@app.get("/execute_config")
async def execute_config(request: Request):
    return templates.TemplateResponse("execute_config.html", {"request": request})


# Route to perform validation
@app.post("/validate")
async def validate_input(request: Request):
    """
    This route receives the validation request in JSON format, including
    the field name, its value, and the list of validations to run.
    It dynamically calls the appropriate method from ConfigValidator and returns the result.
    """
    try:
        # Parse the JSON request body
        data = await request.json()
        field = data.get("field")
        value = data.get("value")
        validations = data.get("validations", [])

        # Ensure all necessary data is present
        if not field or value is None or not validations:
            return JSONResponse(content={"error": "Invalid request: missing field, value, or validations."}, status_code=400)

        # Try to convert strings that appear as numbers to integers
        if isinstance(value, str):
            try:
                # Attempt to convert to integer if possible
                if value.isdigit():
                    value = int(value)
            except ValueError:
                pass  # If it can't be converted, keep it as a string

        # Handle the case where lists of integers are expected but provided as a string (e.g., "123,456")
        if isinstance(value, str) and "," in value:
            try:
                value = [int(v.strip()) for v in value.split(",")]
            except ValueError:
                return JSONResponse(content={"error": f"Invalid format for list of integers: {value}"}, status_code=400)

        # Check if the validation expects a list and convert if necessary
        for validation in validations:
            if isinstance(validation, str):
                # Handle simple validation where only the name is given
                validation_name = validation
                validation_params = {}
            elif isinstance(validation, dict):
                # Handle complex validation with parameters
                validation_name, validation_params = next(iter(validation.items()))
            else:
                return JSONResponse(content={"error": "Invalid validation format."}, status_code=400)

            # Dynamically get the validation method from ConfigValidator
            validator = getattr(ConfigValidator, validation_name, None)

            if not validator:
                return JSONResponse(content={"error": f"Validation method '{validation_name}' not found"}, status_code=400)

            # Convert single integers to lists if the validation expects a list
            if validation_name in ["validate_int_list", "validate_int_list_digits"] and isinstance(value, int):
                value = [value]  # Wrap single integer in a list

            # Call the validation method with the field and value
            validator(field, value, **validation_params)

        return JSONResponse(content={"success": True})  # Return success if no exceptions are raised
    except ValueError as e:
        # Catch validation errors and return the error message
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        # Catch any other errors
        return JSONResponse(content={"error": f"Unexpected error: {str(e)}"}, status_code=500)
