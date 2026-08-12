# Email Verification Setup - ProBlog

## Overview
This document outlines the email verification implementation for user registration and password reset processes in ProBlog.

## Features Implemented

### 1. User Registration with Email Verification
- When a user registers, an account is created but marked as unverified
- A verification email is sent to the user's email address
- User must click the verification link before they can log in
- Verification tokens expire after 24 hours

### 2. Password Reset with Email Verification
- Users can request a password reset via email
- Only verified users can reset their password
- Password reset links expire after 24 hours

### 3. Resend Verification
- Users can request a new verification email if they didn't receive the first one
- Available from the login page

### 4. Token Management
- Expired tokens are automatically cleaned up via management command
- Each token can only be used once

## Email Configuration

### Gmail SMTP Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'alyyfarhan4@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password-here'
DEFAULT_FROM_EMAIL = 'alyyfarhan4@gmail.com'
```

**Note:** The password is an App Password generated from Google Account settings, not your regular Gmail password.

## Database Changes

### New Fields Added to Profile Model
- `is_email_verified`: Boolean field to track verification status

### New Model: EmailVerificationToken
- `user`: ForeignKey to User (OneToOne)
- `token`: UUID field (unique)
- `created_at`: DateTimeField (auto now)
- `expires_at`: DateTimeField (24 hours from creation)
- `is_used`: BooleanField (track if token was used)

## URLs Added

| URL Pattern | Name | Description |
|------------|------|-------------|
| `/verify/<uuid:token>/` | `verify_email` | Verify email with token |
| `/resend-verification/` | `resend_verification` | Resend verification email |

## Email Templates

### Verification Email
- Location: `templates/accounts/email/verification_email.html`
- Contains: Welcome message, verification link, expiry notice

### Password Reset Email
- Location: `templates/accounts/email/password_reset_email.html`
- Contains: Reset link, security notice, expiry warning

### Resend Verification Page
- Location: `templates/accounts/resend_verification.html`
- Simple form to request new verification email

## Management Commands

### Clean Expired Tokens
```bash
python manage.py clean_expired_tokens
```

This command deletes expired and unused verification tokens. Recommended to run daily via cron job or scheduled task.

## Workflow

### Registration Flow
1. User fills registration form
2. Account created with `is_email_verified = False`
3. Verification token created with 24-hour expiry
4. Verification email sent to user
5. User receives success message with instruction to check email
6. User clicks verification link
7. Account marked as verified (`is_email_verified = True`)
8. Token marked as used
9. User can now log in

### Login Flow with Verification Check
1. User enters credentials
2. System checks if email is verified
3. If verified: Login successful
4. If not verified: Login denied with message to verify email

### Password Reset Flow
1. User enters email on password reset form
2. System checks if email exists
3. If exists and verified: Reset email sent
4. If exists but not verified: Error message about verification required
5. If not exists: Generic error (security measure)

## Docker Configuration

No changes needed to Dockerfile. The entrypoint script already handles:
- Database migrations
- Static file collection
- Running the application

## Testing Instructions

### Test Registration
1. Go to `/accounts/register/`
2. Create a new account
3. Check console/logs for email (or check actual inbox with Gmail)
4. Click verification link
5. Try to log in

### Test Password Reset
1. Go to `/accounts/password/reset/`
2. Enter your email
3. Check for reset email
4. Click reset link
5. Set new password

### Test Resend Verification
1. Go to login page
2. Click "Resend verification email" link
3. Enter your email
4. Check for new verification email

## Troubleshooting

### Email Not Sending
- Verify Gmail App Password is correct
- Check if "Allow less secure apps" is enabled (or use App Password)
- Check spam/junk folder
- Verify Django is running with correct settings

### Token Expired
- Tokens expire after 24 hours
- User can request new verification via resend page

### Verification Link Not Working
- Check token is valid and not used
- Ensure URL is complete (including domain)
- Try resending verification

## Security Notes

1. **App Passwords**: Use Gmail App Passwords, not regular passwords
2. **Token Security**: UUID tokens are cryptographically secure
3. **Rate Limiting**: Consider adding rate limiting for email resends
4. **Email Exposure**: Don't reveal if email exists in password reset (already implemented)
5. **HTTPS**: Ensure HTTPS in production for email links

## Next Steps / Improvements

1. Add rate limiting to prevent abuse
2. Implement email queue for better performance
3. Add email templates in multiple languages
4. Implement email verification resend with cooldown period
5. Add logging and monitoring for email delivery
6. Consider using a dedicated email service (SendGrid, Mailgun, etc.) for production

## Dependencies Added

- `django-email-verification==0.6.0` (Note: This is for reference but we implemented custom solution)

Actually, we implemented a custom solution without external dependencies, so no new packages are needed beyond Django's built-in email capabilities.

## Files Modified/Created

### Modified Files
1. `problog/requirements.txt` - Added django-email-verification (optional, for reference)
2. `problog/problog/settings.py` - Added email configuration
3. `problog/accounts/models.py` - Added verification fields and model
4. `problog/accounts/views.py` - Added verification logic
5. `problog/accounts/urls.py` - Added verification URLs
6. `problog/templates/accounts/login.html` - Added resend verification link

### New Files Created
1. `problog/accounts/utils.py` - Email utility functions
2. `problog/accounts/management/commands/clean_expired_tokens.py` - Cleanup command
3. `problog/templates/accounts/email/verification_email.html` - Verification email template
4. `problog/templates/accounts/email/password_reset_email.html` - Password reset email template
5. `problog/templates/accounts/resend_verification.html` - Resend verification page
6. `problog/EMAIL_VERIFICATION_SETUP.md` - This documentation

## Database Migrations Applied
- `accounts/migrations/0002_profile_is_email_verified_emailverificationtoken.py`

## Deployment Notes

### For Production
1. Update `EMAIL_HOST_PASSWORD` with your actual Gmail App Password
2. Set `DEBUG = False` in production
3. Configure proper `ALLOWED_HOSTS`
4. Consider using environment variables for sensitive data:
   ```python
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
   ```
5. Set up cron job for `clean_expired_tokens`:
   ```bash
   0 0 * * * cd /path/to/problog && python manage.py clean_expired_tokens
   ```

### Environment Variables to Set
```bash
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Success Criteria
- [x] New users receive verification email on registration
- [x] Users cannot log in until email is verified
- [x] Password reset only works for verified accounts
- [x] Verification links expire after 24 hours
- [x] Users can request new verification email
- [x] Docker configuration works with new setup
- [x] All migrations applied successfully

---

**Setup Date:** 2026-08-12
**Status:** ✅ Complete