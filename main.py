"""Main FastAPI application - Clean and modular"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from config.settings import SESSION_SECRET_KEY

# Import routers
from api import page_routes, auth_routes, otp_routes, phone_routes, totp_routes

# Create FastAPI app
app = FastAPI(title="Sports Club Management System")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(page_routes.router, tags=["pages"])
app.include_router(auth_routes.router, tags=["auth"])
app.include_router(otp_routes.router, tags=["otp"])
app.include_router(phone_routes.router, tags=["phone"])
app.include_router(totp_routes.router, tags=["totp"])
