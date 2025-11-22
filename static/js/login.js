const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.textContent = "";
    
    const formData = new FormData(loginForm);
    const data = Object.fromEntries(formData.entries());
    
    // Client-side validation
    if (!data.identifier || !data.password) {
        loginError.textContent = "All fields are required";
        return;
    }
    
    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        
        const result = await response.json();
        
        if (!result.success) {
            loginError.textContent = result.error || "Login failed";
            return;
        }
        
        // Check if TOTP required
        if (result.require_totp) {
            window.location.href = result.redirect; // Redirect to /totp
        } else {
            window.location.href = result.redirect; // Redirect to /sports
        }
        
    } catch (error) {
        loginError.textContent = "Network error. Please try again.";
        console.error("Login error:", error);
    }
});
