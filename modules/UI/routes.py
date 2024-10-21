from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import yaml
import os

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



# # Route to display the configuration form
# @app.get("/config")
# async def config_form(request: Request):
#     config_rules = load_config_rules()  # Load the config rules
#     return config_rules
#     # return templates.TemplateResponse("config_form.html", {"request": request, "config_rules": config_rules})


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
