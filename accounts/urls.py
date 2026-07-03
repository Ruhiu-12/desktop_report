from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("verification-sent",views.verification_sent, name="verification_sent"),
    
    
    path(
        "proceed-to-dashboard", views.proceed_to_dashboard, name="proceed_to_dashboard"
    ),
   
    path("verify/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path(
        "resend_verification",
        views.resend_verification_email,
        name="resend_verification",
    ),
    path("logout", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset/<uidb64>/<token>/", views.reset_password, name="reset_password"),
]
