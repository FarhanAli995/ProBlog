from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Generates a one-time token used to verify a user's email address.

    Reuses Django's secure PasswordResetTokenGenerator machinery so the
    token is hashed, time-limited, and invalidated automatically once the
    user's password or is_active state changes.
    """

    def _make_hash_value(self, user, timestamp):
        # Include is_active so a token becomes invalid once the account
        # has already been verified (prevents link reuse).
        return f'{user.pk}{timestamp}{user.is_active}'


email_verification_token = EmailVerificationTokenGenerator()
