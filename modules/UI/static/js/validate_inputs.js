// Function to validate inputs
async function validateInput(fieldName, fieldValue, validations) {
    try {
        // Handle multiple values, if the input expects a list of values (e.g., comma-separated)
        if (fieldValue.includes(",")) {
            fieldValue = fieldValue.split(",").map(value => value.trim());
        }

        // Prepare the payload for the API
        const payload = {
            field: fieldName,
            value: fieldValue,
            validations: validations
        };

        // Send a POST request to the validation route
        const response = await fetch('/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            console.log(`${fieldName} is valid.`);
        } else {
            console.error(`Validation failed for ${fieldName}: ${result.error}`);
            alert(`Validation Error: ${result.error}`);
        }
    } catch (error) {
        console.error(`Error during validation: ${error}`);
        alert(`Validation Error: ${error.message}`);
    }
}



// Attach event listeners to all input fields
function attachValidationListeners() {
    const form = document.getElementById('config-form');

    // Loop through all input elements
    const inputElements = form.querySelectorAll('input, select');
    inputElements.forEach(inputElement => {
        const fieldName = inputElement.getAttribute('name');
        const validations = inputElement.dataset.validations ? JSON.parse(inputElement.dataset.validations) : [];

        // Attach an event listener to trigger validation on change
        inputElement.addEventListener('change', () => {
            validateInput(fieldName, inputElement.value, validations);
        });
    });
}

// Ensure the listeners are attached when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    attachValidationListeners();
});
