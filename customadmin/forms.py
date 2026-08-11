from django import forms
from django.contrib.auth.models import User, Group, Permission

from accounts.models import Profile
from blogs.models import Blog, Category, Tag, BlogReview
from comments.models import Comment, Report


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every field's widget automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault('class', 'form-control')
            else:
                widget.attrs.setdefault('class', 'form-control')


# ─── Authentication ────────────────────────────────────────────────────────

class UserEditForm(BootstrapModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'is_superuser', 'groups']


class UserCreateForm(BootstrapModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'is_superuser']

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class GroupForm(BootstrapModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').order_by(
            'content_type__app_label', 'codename'
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']


# ─── Accounts ──────────────────────────────────────────────────────────────

class ProfileForm(BootstrapModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'location', 'website']


# ─── Blogs ─────────────────────────────────────────────────────────────────

class BlogForm(BootstrapModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'author', 'category', 'tags', 'excerpt', 'content',
                  'featured_image', 'video_url', 'status', 'is_featured']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
            'excerpt': forms.Textarea(attrs={'rows': 2}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class TagForm(BootstrapModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class BlogReviewForm(BootstrapModelForm):
    class Meta:
        model = BlogReview
        fields = ['blog', 'editor', 'decision', 'feedback']


# ─── Comments ──────────────────────────────────────────────────────────────

class CommentForm(BootstrapModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'is_approved']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }


class ReportForm(BootstrapModelForm):
    class Meta:
        model = Report
        fields = ['status', 'reviewed_by']
