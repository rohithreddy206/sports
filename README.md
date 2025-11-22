# Sports Club Management System

A complete web application for sports club management with advanced authentication features including Email OTP, Phone OTP (Twilio), and TOTP 2FA (Google Authenticator).

---

## 🚀 Features

### Authentication & Security
- ✅ **Email Verification** - OTP sent via SMTP
- ✅ **Phone Verification** - SMS OTP via Twilio Verify API
- ✅ **TOTP 2FA** - Google Authenticator integration
- ✅ **Session Management** - Secure session-based authentication
- ✅ **Password Hashing** - Bcrypt encryption
- ✅ **Email Availability Check** - Real-time validation

### User Management
- ✅ User Registration with dual verification
- ✅ Login with Email/Phone
- ✅ Protected Dashboard
- ✅ Logout functionality

### UI/UX
- ✅ Responsive design
- ✅ Modern gradient interface
- ✅ Real-time form validation
- ✅ Loading states and error handling
- ✅ QR code generation for 2FA setup

---

## 📁 Project Structure

```
new_project/
├── main.py                 # FastAPI application
├── database.py             # SQLite database operations
├── requirements.txt        # Python dependencies
├── templates/
│   ├── registration.html   # Registration page
│   ├── login.html          # Login page
│   └── sports.html         # Dashboard
└── static/
    ├── css/
    │   └── styles.css      # Styles
    └── js/
        ├── register.js     # Registration logic
        └── login.js        # Login logic
```

## Technologies

- **Backend**: Python FastAPI
- **Database**: SQLite
- **Templating**: Jinja2
- **Authentication**: Session-based with PassLib (bcrypt)
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API)
