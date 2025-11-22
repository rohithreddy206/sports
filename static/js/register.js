const regForm = document.getElementById("registrationForm");
const regError = document.getElementById("regError");
const submitBtn = document.getElementById("submitBtn");
const btnText = document.getElementById("btnText");
const btnSpinner = document.getElementById("btnSpinner");

// Email verification variables
let emailVerified = false;
let verifiedEmail = "";

const emailInput = document.getElementById("email");
const sendEmailOtpBtn = document.getElementById("sendEmailOtpBtn");
const emailOtpInput = document.getElementById("emailOtpInput");
const emailOtpCode = document.getElementById("emailOtpCode");
const verifyEmailOtpBtn = document.getElementById("verifyEmailOtpBtn");
const emailVerifiedBadge = document.getElementById("emailVerifiedBadge");
const emailVerifyError = document.getElementById("emailVerifyError");

// Phone verification variables
let phoneVerified = false;
let verifiedPhoneNumber = "";

const phoneInput = document.getElementById("phone");
const sendPhoneOtpBtn = document.getElementById("sendPhoneOtpBtn");
const otpVerifyInput = document.getElementById("otpVerifyInput");
const phoneOtpCode = document.getElementById("phoneOtpCode");
const verifyPhoneOtpBtn = document.getElementById("verifyPhoneOtpBtn");
const phoneVerifiedBadge = document.getElementById("phoneVerifiedBadge");
const phoneVerifyError = document.getElementById("phoneVerifyError");

// Check if both verifications are complete
function checkBothVerifications() {
    if (emailVerified && phoneVerified) {
        submitBtn.disabled = false;
    }
}

// Send Email OTP
async function sendEmailOTP() {
    const email = emailInput.value.trim();
    
    emailVerifyError.textContent = "";
    
    if (!email) {
        emailVerifyError.textContent = "Please enter your email";
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        emailVerifyError.textContent = "Please enter a valid email";
        return;
    }
    
    sendEmailOtpBtn.disabled = true;
    sendEmailOtpBtn.textContent = "Sending...";
    
    try {
        const response = await fetch("/send_email_otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                email,
                first_name: document.getElementById("first_name").value || "User",
                last_name: document.getElementById("last_name").value || "",
                phone: phoneInput.value || "+1234567890",
                password: "temp123",
                confirm_password: "temp123"
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            emailOtpInput.classList.add("show");
            emailOtpCode.focus();
            sendEmailOtpBtn.textContent = "Resend Email OTP";
            emailVerifyError.style.color = "#10b981";
            emailVerifyError.textContent = "OTP sent to your email";
        } else {
            emailVerifyError.textContent = result.error || "Failed to send OTP";
        }
    } catch (error) {
        emailVerifyError.textContent = "Network error. Please try again.";
        console.error("Send Email OTP error:", error);
    } finally {
        sendEmailOtpBtn.disabled = false;
    }
}

// Verify Email OTP
async function verifyEmailOTP() {
    const otp = emailOtpCode.value.trim();
    
    emailVerifyError.textContent = "";
    
    if (!otp || otp.length !== 6) {
        emailVerifyError.textContent = "Please enter 6-digit OTP";
        return;
    }
    
    verifyEmailOtpBtn.disabled = true;
    verifyEmailOtpBtn.textContent = "Verifying...";
    
    try {
        const response = await fetch("/verify_email_otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ otp })
        });
        
        const result = await response.json();
        
        if (result.success) {
            emailVerified = true;
            verifiedEmail = emailInput.value.trim();
            emailVerifiedBadge.classList.add("show");
            emailOtpInput.style.display = "none";
            sendEmailOtpBtn.style.display = "none";
            emailInput.setAttribute('readonly', 'readonly');
            emailInput.style.backgroundColor = "#f3f4f6";
            emailInput.style.cursor = "not-allowed";
            emailVerifyError.textContent = "";
            
            checkBothVerifications();
        } else {
            emailVerifyError.textContent = result.error || "Invalid OTP";
            emailOtpCode.value = "";
            emailOtpCode.focus();
        }
    } catch (error) {
        emailVerifyError.textContent = "Verification failed. Please try again.";
        console.error("Verify Email OTP error:", error);
    } finally {
        verifyEmailOtpBtn.disabled = false;
        verifyEmailOtpBtn.textContent = "Verify Email OTP";
    }
}

// Send Phone OTP
async function sendPhoneOTP() {
    const phone = phoneInput.value.trim();
    
    phoneVerifyError.textContent = "";
    
    if (!phone) {
        phoneVerifyError.textContent = "Please enter your phone number";
        phoneVerifyError.style.color = "#ef4444";
        return;
    }
    
    sendPhoneOtpBtn.disabled = true;
    sendPhoneOtpBtn.textContent = "Sending...";
    
    try {
        const response = await fetch("/send-phone-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone })
        });
        
        const result = await response.json();
        
        if (result.success) {
            otpVerifyInput.classList.add("show");
            phoneOtpCode.focus();
            sendPhoneOtpBtn.textContent = "Resend OTP";
            phoneVerifyError.style.color = "#10b981";
            phoneVerifyError.textContent = result.message;
        } else {
            phoneVerifyError.textContent = result.error || "Failed to send OTP";
            phoneVerifyError.style.color = "#ef4444";
        }
    } catch (error) {
        phoneVerifyError.textContent = "Network error. Please try again.";
        phoneVerifyError.style.color = "#ef4444";
        console.error("Send OTP error:", error);
    } finally {
        sendPhoneOtpBtn.disabled = false;
    }
}

// Verify Phone OTP
async function verifyPhoneOTP() {
    const phone = phoneInput.value.trim();
    const otp = phoneOtpCode.value.trim();
    
    phoneVerifyError.textContent = "";
    
    if (!otp || otp.length !== 6) {
        phoneVerifyError.textContent = "Please enter 6-digit OTP";
        phoneVerifyError.style.color = "#ef4444";
        return;
    }
    
    verifyPhoneOtpBtn.disabled = true;
    verifyPhoneOtpBtn.textContent = "Verifying...";
    
    try {
        const response = await fetch("/verify-phone-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone, otp })
        });
        
        const result = await response.json();
        
        if (result.success) {
            phoneVerified = true;
            verifiedPhoneNumber = phone;
            phoneVerifiedBadge.classList.add("show");
            otpVerifyInput.style.display = "none";
            sendPhoneOtpBtn.style.display = "none";
            phoneInput.setAttribute('readonly', 'readonly');
            phoneInput.style.backgroundColor = "#f3f4f6";
            phoneInput.style.cursor = "not-allowed";
            phoneVerifyError.textContent = "";
            
            checkBothVerifications();
        } else {
            phoneVerifyError.textContent = result.error || "Invalid OTP";
            phoneVerifyError.style.color = "#ef4444";
            phoneOtpCode.value = "";
            phoneOtpCode.focus();
        }
    } catch (error) {
        phoneVerifyError.textContent = "Verification failed. Please try again.";
        phoneVerifyError.style.color = "#ef4444";
        console.error("Verify OTP error:", error);
    } finally {
        verifyPhoneOtpBtn.disabled = false;
        verifyPhoneOtpBtn.textContent = "Verify OTP";
    }
}

// Only allow numbers in OTP inputs
if (emailOtpCode) {
    emailOtpCode.addEventListener("input", (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, "");
    });
}

if (phoneOtpCode) {
    phoneOtpCode.addEventListener("input", (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, "");
    });
}

// Event listeners
if (sendEmailOtpBtn) {
    sendEmailOtpBtn.addEventListener("click", sendEmailOTP);
}
if (verifyEmailOtpBtn) {
    verifyEmailOtpBtn.addEventListener("click", verifyEmailOTP);
}
if (sendPhoneOtpBtn) {
    sendPhoneOtpBtn.addEventListener("click", sendPhoneOTP);
}
if (verifyPhoneOtpBtn) {
    verifyPhoneOtpBtn.addEventListener("click", verifyPhoneOTP);
}

// Modified form submission handler
regForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    regError.textContent = "";
    emailVerifyError.textContent = "";
    phoneVerifyError.textContent = "";
    
    // Check both verifications
    if (!emailVerified) {
        regError.textContent = "Please verify your email first";
        emailVerifyError.textContent = "Please verify your email first";
        return;
    }
    
    if (!phoneVerified) {
        regError.textContent = "Please verify your phone number first";
        phoneVerifyError.textContent = "Please verify your phone number first";
        phoneVerifyError.style.color = "#ef4444";
        return;
    }
    
    const formData = new FormData(regForm);
    const data = Object.fromEntries(formData.entries());
    
    // Use verified email and phone
    data.email = verifiedEmail;
    data.phone = verifiedPhoneNumber;
    
    // Remove otp fields
    delete data.otp;
    
    // Client-side validation
    const requiredFields = ["first_name", "last_name", "password", "confirm_password"];
    for (const field of requiredFields) {
        if (!data[field] || data[field].trim() === "") {
            regError.textContent = `${field.replace('_', ' ')} is required`;
            return;
        }
    }
    
    if (data.password !== data.confirm_password) {
        regError.textContent = "Passwords do not match";
        return;
    }
    
    if (data.password.length < 6) {
        regError.textContent = "Password must be at least 6 characters long";
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    btnText.style.display = "none";
    btnSpinner.style.display = "inline";
    
    try {
        const response = await fetch("/verify_phone_otp_and_register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        
        const result = await response.json();
        
        if (!result.success) {
            regError.textContent = result.error || "Registration failed";
            submitBtn.disabled = false;
            btnText.style.display = "inline";
            btnSpinner.style.display = "none";
            return;
        }
        
        // Success - check if redirecting to TOTP setup or login
        if (result.redirect === "/totp-setup") {
            // Show success message about 2FA setup
            alert("✅ " + result.message);
        }
        
        window.location.href = result.redirect;
        
    } catch (error) {
        regError.textContent = "Network error. Please try again.";
        console.error("Registration error:", error);
        submitBtn.disabled = false;
        btnText.style.display = "inline";
        btnSpinner.style.display = "none";
    }
});

// FIXED: Email availability check
const emailErrorDiv = document.getElementById("email-error");
let emailAvailable = false;
let emailChecked = false;

async function checkEmailAvailability(email) {
    emailChecked = false;
    
    if (!email || email.trim() === "") {
        if (emailErrorDiv) {
            emailErrorDiv.style.display = "none";
        }
        emailAvailable = false;
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        if (emailErrorDiv) {
            emailErrorDiv.textContent = "Invalid email format";
            emailErrorDiv.style.display = "block";
        }
        emailAvailable = false;
        return;
    }
    
    try {
        const response = await fetch(`/check-email?email=${encodeURIComponent(email)}`);
        const result = await response.json();
        
        emailChecked = true;
        
        // If email EXISTS (exists=true), it's NOT available
        if (result.exists === true || result.available === false) {
            if (emailErrorDiv) {
                emailErrorDiv.textContent = result.message || "Email already registered. Please use a different email.";
                emailErrorDiv.style.display = "block";
            }
            emailAvailable = false;
            
            // Disable send email OTP button if email exists
            if (sendEmailOtpBtn) {
                sendEmailOtpBtn.disabled = true;
            }
        } 
        // If email does NOT exist (exists=false), it IS available
        else if (result.exists === false && result.available === true) {
            if (emailErrorDiv) {
                emailErrorDiv.style.display = "none";
            }
            emailAvailable = true;
            
            // Enable send email OTP button
            if (sendEmailOtpBtn) {
                sendEmailOtpBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error("Error checking email:", error);
        if (emailErrorDiv) {
            emailErrorDiv.textContent = "Error checking email availability";
            emailErrorDiv.style.display = "block";
        }
        emailAvailable = false;
        emailChecked = false;
    }
}

// Check email on blur (when user leaves the field)
if (emailInput) {
    emailInput.addEventListener("blur", (e) => {
        const email = e.target.value.trim();
        if (email && !emailVerified) {
            checkEmailAvailability(email);
        }
    });
    
    // Clear error and reset when user types
    emailInput.addEventListener("input", (e) => {
        if (emailErrorDiv) {
            emailErrorDiv.style.display = "none";
        }
        emailAvailable = false;
        emailChecked = false;
        
        if (sendEmailOtpBtn && !emailVerified) {
            sendEmailOtpBtn.disabled = false;
        }
    });
}

// Update Send Email OTP to check availability first
const originalSendEmailOTP = sendEmailOTP;
sendEmailOTP = async function() {
    const email = emailInput.value.trim();
    
    // Check email availability before sending OTP
    await checkEmailAvailability(email);
    
    if (!emailAvailable && emailChecked) {
        emailVerifyError.textContent = "Email already registered. Please use a different email.";
        if (emailErrorDiv) {
            emailErrorDiv.textContent = "Email already registered. Please use a different email.";
            emailErrorDiv.style.display = "block";
        }
        return;
    }
    
    // Continue with original send email OTP logic
    return originalSendEmailOTP.call(this);
};

// Update form submission validation
const formSubmitHandler = regForm.querySelector('button[type="submit"]');
if (formSubmitHandler) {
    regForm.addEventListener("submit", async (e) => {
        // If email not verified, check availability
        if (!emailVerified) {
            const email = emailInput.value.trim();
            await checkEmailAvailability(email);
            
            if (!emailAvailable) {
                e.preventDefault();
                e.stopPropagation();
                regError.textContent = "Please use a different email address";
                if (emailErrorDiv) {
                    emailErrorDiv.textContent = "This email is already registered";
                    emailErrorDiv.style.display = "block";
                }
                return false;
            }
        }
    }, true); // Capture phase
}
