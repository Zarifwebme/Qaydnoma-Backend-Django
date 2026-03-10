from config import settings
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

class ThrottledPasswordResetView(PasswordResetView):
    throttle_scope = "password_reset"

    # def get_email_options(self):
    #     return {
    #         "password_reset_confirm_url": f"{settings.FRONTEND_URL}/reset-password.html?uid={{uid}}&token={{token}}"
    #     }

class ThrottledPasswordResetConfirmView(PasswordResetConfirmView):
    throttle_scope = "password_reset"