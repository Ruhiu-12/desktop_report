from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model


from django.http import HttpResponse
from datetime import datetime

# Import your custom tokens and forms
from .tokens import account_activation_token, password_reset_token
from .forms import UserRegistrationForm

# Reference the custom user model defined in your project
User = get_user_model()

# Registration view
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user but don't save to DB yet
            user = form.save(commit=False)
            user.is_active = True
            user.is_verified = False  # Ensure user cannot log in until verified
            user.set_password(form.cleaned_data["password"])
            user.save()
            
            # Trigger the email verification process
            send_verification_email(request, user)
            
            messages.success(request, "Account created! Please check your email to verify.")
            return redirect("verification_sent")
    else:
        form = UserRegistrationForm()
        
    return render(request, "accounts/register.html", {"form": form})

# Helper function to send the activation email
def send_verification_email(request, user):
    current_site = get_current_site(request)
    subject = "Verify your account"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    
    html_message = render_to_string("emails/verification_email.html", {
        "user": user,
        "domain": current_site.domain,
        "uid": uid,
        "token": token,
    })
    
    email = EmailMessage(
        subject,
        html_message,  # Content
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    email.content_subtype = "html"  # This is the important part!
    email.send()

    # Verify email logic


def verification_sent(request):
    return render(request, 'accounts/verification_sent.html')

def proceed_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        messages.error(request, "You must be logged in to access the dashboard.")
        return redirect("login")


def verify_email(request, uidb64, token):
    try:
        # Decode the user's Primary Key from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the token is valid for this user
    if user and account_activation_token.check_token(user, token):
        # Successfully verified: flip the switch
        user.is_verified = True
        user.is_active = True  # Optionally activate the user if you want them to log in immediately
        user.save()
        
        # Log the user in automatically after verification
        auth_login(request, user)
        
        
        return render(request, "accounts/activation_invalid.html")
    

# Resend Verification token
def resend_verification_email(request):
    email = request.GET.get("email") or request.POST.get("email")
    if not email:
        messages.error(request, "Email is required.")
        return redirect("verification_sent")
    
    try:
        user = User.objects.get(email=email)
        
        # Check if the user is already verified
        if user.is_verified:
            messages.info(request, "This account is already verified. Please log in.")
            return redirect("login")
        
        # Generate a new token and send the email
        send_verification_email(request, user)
        
        messages.success(request, f"A new verification email has been sent to {user.email}.")
        return redirect("verification_sent")
        
    except User.DoesNotExist:
        messages.error(request, "No account found with this email.")
        return redirect("register")
    


    # Forgot Password: Request reset link
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect("forgot_password")
        
        # Prepare reset token
        current_site = get_current_site(request)
        subject = "Reset your password"
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)
        protocol = "https" if request.is_secure() else "http"
        
        message = render_to_string("emails/reset_password_email.html", {
            "user": user,
            "domain": current_site.domain,
            "protocol": protocol,
            "uid": uidb64,
            "token": token,
        })
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        messages.success(request, "Password reset email sent. Check your inbox.")
        return redirect("login")
        
    return render(request, "accounts/forgot_password.html")

# Reset Password: Handle form submission
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and password_reset_token.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)
            
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successful. You can now log in.")
            return redirect("login")
        return render(request, "accounts/reset_password.html", {"validlink": True})
    else:
        messages.error(request, "This reset link is invalid or has expired.")
        return render(request, "accounts/reset_password.html", {"validlink": False})


#     # --- 2FA & Recovery Logic ---

# @login_required
# def second_authentication(request):
#     """View to verify the 2FA token."""
#     if request.method == "POST":
#         token = request.POST.get("otp_token")
#         totp = pyotp.TOTP(request.user.otp_secret)
#         if totp.verify(token):
#             request.session['2fa_verified'] = True
#             return redirect("dashboard_dispatcher")
#         else:
#             messages.error(request, "Invalid 2FA token.")
#     return render(request, "accounts/second_auth.html")

# @login_required
# def setup_new_2fa(request):
#     """Generate a new 2FA secret and display a QR code."""
#     if not request.user.otp_secret:
#         request.user.otp_secret = pyotp.random_base32()
#         request.user.save()
    
#     uri = pyotp.totp.TOTP(request.user.otp_secret).provisioning_uri(
#         name=request.user.email, issuer_name="ChainProof"
#     )
#     img = qrcode.make(uri)
#     buf = io.BytesIO()
#     img.save(buf)
#     qr_code = base64.b64encode(buf.getvalue()).decode()
    
#     return render(request, "accounts/setup_2fa.html", {"qr_code": qr_code})

# @login_required
# def download_recovery_codes(request):
#     """Generate and provide PDF recovery codes."""
#     # Generate 5 secure recovery codes
#     codes = [secrets.token_hex(8) for _ in range(5)]
#     request.user.recovery_codes = json.dumps(codes)
#     request.user.save()
    
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="recovery_codes.pdf"'
    
#     p = canvas.Canvas(response, pagesize=letter)
#     p.drawString(100, 750, "ChainProof Recovery Codes")
#     for i, code in enumerate(codes):
#         p.drawString(100, 700 - (i*30), f"Code {i+1}: {code}")
#     p.showPage()
#     p.save()
#     return response

   


    # Login view
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")
        
        try:
            # Check if user exists by their identifier
            user = User.objects.get(identifier=identifier)
            
            # Security Gate: Ensure the user is verified before allowing access
            if not user.is_verified:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect("verification_sent")
            
            # Authenticate the user[cite: 4]
            user = authenticate(request, identifier=identifier, password=password)
            
            if user is not None:
                auth_login(request, user)
                # Redirect to the dispatcher to handle role-based routing
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid identifier or password.")
                return redirect("login")
                
        except User.DoesNotExist:
            messages.error(request, "No account found with this identifier.")
            return redirect("login")
            
    return render(request, "accounts/login.html")

# Logout view
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You’ve been logged out successfully.")
    else:
        messages.info(request, "You’re not logged in.")
    return redirect("login")

# Dashboard Dispatcher
@login_required
def dashboard(request):
    # Route Superusers to the native Django Admin panel
    if request.user.is_superuser:
        return redirect("/admin/")
    
    # Route based on user group membership
    if request.user.groups.filter(name='analyst').exists():
        return redirect("reports:dashboard")
    
    elif request.user.groups.filter(name='technician').exists():
        return redirect("custody:dashboard")
    
    elif request.user.groups.filter(name='investigator').exists():
        return redirect("cases:case_list")
    
    else:
        # Default fallback for users without specific roles
        return redirect("dashboard:dashboard")






       