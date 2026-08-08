from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
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
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomLoginForm
from .models import Profile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
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
        messages.success(
            self.request,
            'Your account has been created! You can now log in.'
        )
        return response


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
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('accounts:login')
    return render(request, 'accounts/delete_account.html')