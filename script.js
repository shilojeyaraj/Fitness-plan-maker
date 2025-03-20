const API_URL = "http://127.0.0.1:8080";

document.getElementById("fitnessForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    // Show loading state
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "Loading...";
    
    // Collect user input
    const requestData = {
        age: parseInt(document.getElementById("age").value),
        weight: parseFloat(document.getElementById("weight").value),
        height: parseFloat(document.getElementById("height").value),
        goal: document.getElementById("goal").value,
        dietary_restrictions: document.getElementById("diet").value
    };

    try {
        const response = await fetch(`${API_URL}/generate_plan`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Display the AI-generated plan
        const resultDiv = document.getElementById("result");
        resultDiv.innerText = data.plan;
        resultDiv.style.display = "block";
    } catch (error) {
        console.error("Error:", error);
        alert("Error generating fitness plan. Please try again.");
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = "Submit";
    }
});

