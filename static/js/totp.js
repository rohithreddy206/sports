const totpForm = document.getElementById("totpForm");
const totpError = document.getElementById("totpError");
const tokenInput = document.getElementById("token");
const verifyBtn = document.getElementById("verifyBtn");
const verifyText = document.getElementById("verifyText");
const verifySpinner = document.getElementById("verifySpinner");

// Auto-focus token input
tokenInput.focus();

// Only allow numbers in token input
tokenInput.addEventListener("input", (e) => {
    e.target.value = e.target.value.replace(/[^0-9]/g, "");
    
    // Auto-submit when 6 digits entered
    if (e.target.value.length === 6) {
        totpForm.dispatchEvent(new Event("submit"));
    }
});

// Submit TOTP form
totpForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    totpError.textContent = "";
    
    const token = tokenInput.value.trim();
    
    if (!token || token.length !== 6) {
        totpError.textContent = "Please enter a valid 6-digit code";
        return;
    }
    
    // Disable button and show loading
    verifyBtn.disabled = true;
    verifyText.style.display = "none";
    verifySpinner.style.display = "inline";
    
    try {
        const response = await fetch("/totp/verify-login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token }),
        });
        
        const result = await response.json();
        
        if (!result.success) {
            totpError.textContent = result.error || "Invalid code";
            verifyBtn.disabled = false;
            verifyText.style.display = "inline";
            verifySpinner.style.display = "none";
            tokenInput.value = "";
            tokenInput.focus();
            return;
        }
        
        // Success - redirect to dashboard
        window.location.href = result.redirect;
        
    } catch (error) {
        totpError.textContent = "Network error. Please try again.";
        console.error("TOTP verification error:", error);
        verifyBtn.disabled = false;
        verifyText.style.display = "inline";
        verifySpinner.style.display = "none";
    }
});

// Handle paste event for better UX
tokenInput.addEventListener("paste", (e) => {
    e.preventDefault();
    const paste = (e.clipboardData || window.clipboardData).getData("text");
    const cleaned = paste.replace(/[^0-9]/g, "").slice(0, 6);
    tokenInput.value = cleaned;
    
    if (cleaned.length === 6) {
        totpForm.dispatchEvent(new Event("submit"));
    }
});
