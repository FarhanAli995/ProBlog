from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django_ratelimit.core import is_ratelimited
from django.core.exceptions import PermissionDenied
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomLoginForm
from .models import Profile, EmailVerificationToken
from .utils import send_verification_email, send_password_reset_email
import uuid


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # Apply rate limiting for POST requests
        if request.method == 'POST':
            if is_ratelimited(request, group='login', fn='login', key='ip', rate='5/m', method='POST', increment=True):
                messages.error(request, 'Too many login attempts. Please try again later.')
                raise PermissionDenied("Rate limit exceeded. Too many login attempts.")
        
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return next_url
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        user = form.get_user()
        
        # Check if email is verified
        if not user.profile.is_email_verified:
            messages.error(
                self.request,
                'Invalid credentials.'
            )
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        
        messages.success(self.request, f'Welcome back, {user.username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create verification token
        token = EmailVerificationToken.objects.create(user=self.object)
        
        # Send verification email
        email_sent = send_verification_email(self.request, self.object, token.token)
        
        if email_sent:
            messages.success(
                self.request,
                'Account created! Please check your email to verify your account before logging in.'
            )
        else:
            messages.warning(
                self.request,
                'Account created but we could not send verification email. Please contact support.'
            )
        
        return response


def verify_email(request, token):
    """Verify user email with token"""
    try:
        # token is already a UUID object from the URL converter
        token_obj = EmailVerificationToken.objects.get(token=token)
        
        if token_obj.is_valid():
            # Mark user as verified
            profile = token_obj.user.profile
            profile.is_email_verified = True
            profile.save()
            
            # Mark token as used
            token_obj.is_used = True
            token_obj.save()
            
            messages.success(request, 'Your email has been verified successfully! You can now log in.')
            return redirect('accounts:login')
        else:
            if token_obj.is_used:
                messages.error(request, 'This verification link has already been used.')
            else:
                messages.error(request, 'This verification link has expired. Please request a new one.')
            return redirect('accounts:login')
            
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:login')
    except ValueError:
        messages.error(request, 'Invalid verification token.')
        return redirect('accounts:login')


def resend_verification(request):
    """Resend verification email"""
    if request.method == 'POST':
        # Apply rate limiting for POST requests
        if is_ratelimited(request, group='resend_verification', fn='resend_verification', key='ip', rate='3/m', method='POST', increment=True):
            messages.error(request, 'Too many requests. Please try again later.')
            return render(request, 'accounts/resend_verification.html')
        
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.profile.is_email_verified:
                messages.success(request, 'If an account exists with this email, a verification link has been sent.')
                return redirect('accounts:login')
            
            # Delete old token and create new one
            EmailVerificationToken.objects.filter(user=user).delete()
            token = EmailVerificationToken.objects.create(user=user)
            
            email_sent = send_verification_email(request, user, token.token)
            if email_sent:
                messages.success(request, 'If an account exists with this email, a verification link has been sent.')
            else:
                messages.error(request, 'Failed to send verification email. Please try again later.')
            
        except User.DoesNotExist:
            messages.success(request, 'If an account exists with this email, a verification link has been sent.')
        
        return redirect('accounts:login')
    
    return render(request, 'accounts/resend_verification.html')


class ProfileDetailView(DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['profile'] = user.profile
        
        from blogs.models import Blog
        from interactions.models import Follow
        
        # Get published blogs of the profile owner
        published_blogs = user.blogs.filter(status=Blog.STATUS_PUBLISHED).order_by('-published_at')
        context['blogs'] = published_blogs
        context['blogs_count'] = published_blogs.count()
        
        # Follower and Following counts
        context['followers_count'] = user.followers.count()
        context['following_count'] = user.following.count()
        
        # Check if the logged-in user is following the profile owner
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user, following=user
            ).exists()
        else:
            context['is_following'] = False
            
        return context


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Edit Profile'
    }
    return render(request, 'accounts/profile_edit.html', context)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:login')

    def get_success_url(self):
        messages.success(self.request, 'Your password has been changed successfully.')
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your registered email'
        })
        return form
    
    # Removed custom form_valid to prevent user enumeration - Django's built-in already handles this securely


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Incorrect password. Account not deleted.')
    return render(request, 'accounts/delete_account.html')