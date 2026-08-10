from django import forms
from .models import Blog, Category, Tag


class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkboxes'}),
    )

    class Meta:
        model = Blog
        fields = ['title', 'category', 'tags', 'excerpt', 'content', 'featured_image', 'video_url']
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
