from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from .models import Blog, Category, Tag


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def to_python(self, data):
        if data in self.empty_values:
            return []
        if isinstance(data, list):
            return [super().to_python(item) for item in data]
        return [super().to_python(data)]

    def validate(self, data):
        if self.required and not data:
            raise ValidationError(self.error_messages['required'], code='required')
        for uploaded in data:
            super(forms.FileField, self).validate(uploaded)

    def run_validators(self, value):
        for uploaded in value:
            super(forms.FileField, self).run_validators(uploaded)


class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkboxes'}),
    )

    class Meta:
        model = Blog
        fields = ['title', 'category', 'tags', 'excerpt', 'content', 'featured_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a compelling title…',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short summary shown in listings (max 300 chars)…',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your blog post here…',
                'id': 'blog-content',
            }),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Allow multiple images/videos to be uploaded alongside the post
    media = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={
            'multiple': True,
            'accept': 'image/*,video/*',
            'class': 'form-control',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '— No Category —'
        self.fields['category'].required = False
        self.fields['content'].required = True

    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        if image and hasattr(image, 'size'):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be smaller than 5 MB.')
        return image

    def clean_media(self):
        files = self.cleaned_data.get('media', [])
        cleaned = []
        for f in files:
            content_type = getattr(f, 'content_type', '')
            size = getattr(f, 'size', 0)
            if content_type.startswith('image/'):
                if size > 5 * 1024 * 1024:
                    raise forms.ValidationError('Each image must be smaller than 5 MB.')
            elif content_type.startswith('video/'):
                if size > 50 * 1024 * 1024:
                    raise forms.ValidationError('Each video must be smaller than 50 MB.')
            else:
                raise forms.ValidationError('Only image and video files are allowed.')
            cleaned.append(f)
        return cleaned


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag name'}),
        }


class ReviewForm(forms.Form):
    """Editor review decision form."""
    DECISION_CHOICES = [
        ('APPROVED', 'Approve & Publish'),
        ('CHANGES_REQUESTED', 'Request Changes'),
        ('REJECTED', 'Reject'),
    ]
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Feedback for the author (required for changes/rejection)…',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        decision = cleaned.get('decision')
        feedback = cleaned.get('feedback', '').strip()
        if decision in ('CHANGES_REQUESTED', 'REJECTED') and not feedback:
            raise forms.ValidationError('Please provide feedback when requesting changes or rejecting.')
        return cleaned
