const API_URL = "http://127.0.0.1:8000/simplify";

const documentInput = document.getElementById("documentInput");
const simplifyBtn = document.getElementById("simplifyBtn");
const statusMessage = document.getElementById("statusMessage");
const resultsDiv = document.getElementById("results");
const finalText = document.getElementById("finalText");
const extractedPoints = document.getElementById("extractedPoints");
const verificationResult = document.getElementById("verificationResult");

simplifyBtn.addEventListener("click", async () => {
    const text = documentInput.value.trim();

    if (text === "") {
        statusMessage.textContent = "Please paste some text first.";
        return;
    }

    resultsDiv.style.display = "none";
    statusMessage.textContent = "Processing... this can take 15-30 seconds.";
    simplifyBtn.disabled = true;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        finalText.textContent = data.final_text;
        extractedPoints.textContent = data.extracted_points;
        verificationResult.textContent = data.verification_result;

        resultsDiv.style.display = "block";
        statusMessage.textContent = "";

    } catch (error) {
        statusMessage.textContent = "Something went wrong: " + error.message;
        console.error(error);
    } finally {
        simplifyBtn.disabled = false;
    }
});