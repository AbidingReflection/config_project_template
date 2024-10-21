async function populateConfigTemplate() {
    // Fetch the config rules from the API endpoint
    const response = await fetch('/config_rules');
    const configRules = await response.json();

    const form = document.getElementById('config-form');

    // Loop through each field in the config rules and create form elements
    for (const [field, rules] of Object.entries(configRules)) {
        const fieldContainer = document.createElement('div');  // Container for each field
        fieldContainer.setAttribute('class', 'field-container');

        const label = document.createElement('label');
        label.setAttribute('for', field);
        label.textContent = field.replace('_', ' ').capitalize();

        let inputElement;

        // Check for tags and handle "authentication_file_lookup" tag
        if (rules.tags && rules.tags.includes("authentication_file_lookup")) {
            // Fetch the list of authentication files and create a dropdown
            inputElement = document.createElement('select');
            inputElement.setAttribute('id', field);
            inputElement.setAttribute('name', field);

            try {
                const authFilesResponse = await fetch('/auth_files');
                const authFiles = await authFilesResponse.json();

                authFiles.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file;
                    option.textContent = file;
                    inputElement.appendChild(option);
                });

                // Handle case where no files are found
                if (authFiles.length === 0) {
                    const noFilesOption = document.createElement('option');
                    noFilesOption.value = "";
                    noFilesOption.textContent = "No authentication files found";
                    inputElement.appendChild(noFilesOption);
                }
            } catch (error) {
                console.error("Failed to fetch authentication files", error);
            }
        } else if (rules.validation) {
            for (const validation of rules.validation) {
                // Check if allowed_values exists under validate_option
                if (validation.validate_option && validation.validate_option.allowed_values) {
                    // Create a dropdown (select) element for allowed_values
                    inputElement = document.createElement('select');
                    inputElement.setAttribute('id', field);
                    inputElement.setAttribute('name', field);

                    validation.validate_option.allowed_values.forEach(value => {
                        const option = document.createElement('option');
                        option.value = value;
                        option.textContent = value;

                        // Set the default selected option if a default exists
                        if (rules.default && rules.default === value) {
                            option.selected = true;
                        }

                        inputElement.appendChild(option);
                    });

                    // Stop further validation checks once a dropdown is created
                    break;
                }
            }
        }

        // If no allowed_values or tags, default to a text input
        if (!inputElement) {
            inputElement = document.createElement('input');
            inputElement.setAttribute('type', 'text');
            inputElement.setAttribute('id', field);
            inputElement.setAttribute('name', field);

            // Set the default value for the text input if it exists
            if (rules.default) {
                inputElement.setAttribute('value', rules.default);
            }
        }

        // Add 'required' attribute if the field is marked as required
        if (rules.required) {
            inputElement.setAttribute('required', true);
        }

        // Append the label and input element to the form container
        fieldContainer.appendChild(label);
        fieldContainer.appendChild(inputElement);

        // Append the field container to the form
        form.appendChild(fieldContainer);
        form.appendChild(document.createElement('br'));  // Line break for spacing
    }
}

// Helper function to capitalize text
String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

// Call the function to populate the form when the page loads
document.addEventListener('DOMContentLoaded', populateConfigTemplate);
