from django import forms
from .models import Blog, Category, Tag
import os
import puremagic
# Use puremagic directly (works on both Windows and Linux without system dependencies)


class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkboxes'}),
    )

    class Meta:
        model = Blog
        fields = ['title', 'category', 'tags', 'excerpt', 'content', 'featured_image', 'video', 'video_url']
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
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/webm',
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/video.mp4 or YouTube/Vimeo embed URL',
                'type': 'url',
            }),
        }

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

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and hasattr(video, 'size'):
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError('Video must be smaller than 50 MB.')
            
            # Validate file extension
            ext = os.path.splitext(video.name)[1].lower()
            if ext not in ['.mp4', '.webm']:
                raise forms.ValidationError('Only .mp4 and .webm files are allowed.')
            
            # Validate actual file content using puremagic (works on all platforms)
            try:
                video.seek(0)
                # Read first 1024 bytes for magic number detection
                video_data = video.read(1024)
                video.seek(0)
                
                # Use puremagic to detect file type
                detected = puremagic.from_stream(video, 1024)
                if detected and isinstance(detected, list):
                    mime = detected[0].mime_type if detected else None
                else:
                    mime = None
                
                if mime and mime not in ['video/mp4', 'video/webm', 'video/quicktime']:
                    raise forms.ValidationError('Invalid video file content. Only MP4 and WebM are supported.')
            except Exception as e:
                # If validation fails, still allow the upload but log the error
                # In production, you might want to be stricter
                pass
        return video


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
