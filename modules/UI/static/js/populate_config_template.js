async function populateConfigTemplate() {
    // Fetch the config rules from the API endpoint
    const response = await fetch('/config_rules');
    const configRules = await response.json();

    const form = document.getElementById('config-form');

    // Step 1: Group and sort the fields by section and section_order
    const sections = {};

    for (const [field, rules] of Object.entries(configRules)) {
        const sectionName = rules.section || 'General';  // Default to 'General' if no section provided
        const sectionOrder = rules.section_order || 0;

        if (!sections[sectionName]) {
            sections[sectionName] = [];
        }

        sections[sectionName].push({
            field,
            rules,
            order: sectionOrder
        });
    }

    // Sort each section's fields by section_order
    for (const section in sections) {
        sections[section].sort((a, b) => a.order - b.order);
    }

    // Step 2: Render the form fields by section
    for (const section of Object.keys(sections)) {
        // Create a section container
        const sectionContainer = document.createElement('div');
        sectionContainer.setAttribute('class', 'section-container');

        const sectionTitle = document.createElement('h2');
        sectionTitle.textContent = `${section}`;
        sectionContainer.appendChild(sectionTitle);

        // Create the fields within this section
        for (const { field, rules } of sections[section]) {
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

                        break; // Stop further validation checks once a dropdown is created
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

                // Add validation data to the input element for validation purposes
                if (rules.validation) {
                    inputElement.setAttribute('data-validations', JSON.stringify(rules.validation));
                }

                // Attach the input change listener for validation
                inputElement.addEventListener('change', (event) => {
                    validateInput(field, inputElement.value, rules.validation);
                });
            }

            // Add 'required' attribute if the field is marked as required
            if (rules.required) {
                inputElement.setAttribute('required', true);
            }

            // Append the label and input element to the field container
            fieldContainer.appendChild(label);
            fieldContainer.appendChild(inputElement);

            // Check for "accept_multiple_values" tag and add a "+" button
            if (rules.tags && rules.tags.includes("accept_multiple_values")) {
                const addButton = document.createElement('button');
                addButton.type = 'button';
                addButton.textContent = '+';
                addButton.classList.add('add-input-button');
                fieldContainer.appendChild(addButton);

                // Add event listener to dynamically add input fields
                addButton.addEventListener('click', () => {
                    const newInputElement = inputElement.cloneNode();
                    newInputElement.value = '';  // Clear the value for the new input
                    newInputElement.setAttribute('name', `${field}[]`);  // Set name as an array for multiple values
                    fieldContainer.insertBefore(newInputElement, addButton);

                    // Attach validation event to the new input
                    newInputElement.addEventListener('change', (event) => {
                        validateInput(field, newInputElement.value, rules.validation);
                    });
                });
            }

            // Append the field container to the section container
            sectionContainer.appendChild(fieldContainer);
        }

        // Append the section container to the form
        form.appendChild(sectionContainer);
        form.appendChild(document.createElement('hr'));  // Horizontal line between sections
    }

    // Step 3: Create and append the "Save Config" button
    const saveButton = document.createElement('button');
    saveButton.type = 'submit';
    saveButton.textContent = 'Save Config';
    saveButton.classList.add('save-config-button');
    form.appendChild(saveButton);
}

// Helper function to capitalize text
String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

// Call the function to populate the form when the page loads
document.addEventListener('DOMContentLoaded', () => {
    populateConfigTemplate();
});
