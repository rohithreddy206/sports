"""Page rendering routes"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_current_user(request: Request):
    """Get current user from session"""
    from database import get_user_by_id
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/sports", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/email_otp", response_class=HTMLResponse)
async def email_otp_page(request: Request):
    """Display OTP verification page"""
    pending_reg = request.session.get("pending_registration")
    if not pending_reg:
        return RedirectResponse(url="/register", status_code=303)
    
    return templates.TemplateResponse("email_otp.html", {
        "request": request,
        "email": pending_reg.get("email")
    })

@router.get("/sports", response_class=HTMLResponse)
async def sports_dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "sports.html",
        {
            "request": request,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
        },
    )

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
