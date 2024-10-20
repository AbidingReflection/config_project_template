from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

# Route to display the configuration form
@app.get("/config")
async def config_form(request: Request):
    config_rules = load_config_rules()  # Load the config rules
    return templates.TemplateResponse("config_form.html", {"request": request, "config_rules": config_rules})

# Route to create a new configuration
@app.get("/new_config")
async def new_config(request: Request):
    return templates.TemplateResponse("new_config.html", {"request": request})

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
