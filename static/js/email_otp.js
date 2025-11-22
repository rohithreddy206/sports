const otpForm = document.getElementById("otpForm");
const otpError = document.getElementById("otpError");
const otpSuccess = document.getElementById("otpSuccess");
const otpInput = document.getElementById("otp");
const verifyBtn = document.getElementById("verifyBtn");
const verifyText = document.getElementById("verifyText");
const verifySpinner = document.getElementById("verifySpinner");
const resendLink = document.getElementById("resendLink");

// Auto-focus OTP input
otpInput.focus();

// Only allow numbers in OTP input
otpInput.addEventListener("input", (e) => {
    e.target.value = e.target.value.replace(/[^0-9]/g, "");
});

// Submit OTP form
otpForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    otpError.textContent = "";
    otpSuccess.style.display = "none";
    
    const otp = otpInput.value.trim();
    
    if (!otp || otp.length !== 6) {
        otpError.textContent = "Please enter a valid 6-digit OTP";
        return;
    }
    
    // Disable button and show loading
    verifyBtn.disabled = true;
    verifyText.style.display = "none";
    verifySpinner.style.display = "inline";
    
    try {
        const response = await fetch("/verify_email_otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ otp }),
        });
        
        const result = await response.json();
        
        if (!result.success) {
            otpError.textContent = result.error || "Verification failed";
            verifyBtn.disabled = false;
            verifyText.style.display = "inline";
            verifySpinner.style.display = "none";
            otpInput.value = "";
            otpInput.focus();
            return;
        }
        
        // Show success message
        otpSuccess.textContent = result.message || "Email verified successfully! Redirecting...";
        otpSuccess.style.display = "block";
        
        // Redirect to login page
        setTimeout(() => {
            window.location.href = result.redirect;
        }, 1500);
    } catch (error) {
        otpError.textContent = "Network error. Please try again.";
        console.error("OTP verification error:", error);
        verifyBtn.disabled = false;
        verifyText.style.display = "inline";
        verifySpinner.style.display = "none";
    }
});

// Resend OTP
resendLink.addEventListener("click", async (e) => {
    e.preventDefault();
    otpError.textContent = "";
    otpSuccess.style.display = "none";
    
    resendLink.style.pointerEvents = "none";
    resendLink.textContent = "Sending...";
    
    try {
        const response = await fetch("/resend_otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });
        
        const result = await response.json();
        
        if (!result.success) {
            otpError.textContent = result.error || "Failed to resend OTP";
            resendLink.textContent = "Resend OTP";
            resendLink.style.pointerEvents = "auto";
            return;
        }
        
        otpSuccess.textContent = result.message || "OTP sent successfully!";
        otpSuccess.style.display = "block";
        resendLink.textContent = "Resend OTP";
        resendLink.style.pointerEvents = "auto";
        otpInput.value = "";
        otpInput.focus();
    } catch (error) {
        otpError.textContent = "Network error. Please try again.";
        console.error("Resend OTP error:", error);
        resendLink.textContent = "Resend OTP";
        resendLink.style.pointerEvents = "auto";
    }
});
