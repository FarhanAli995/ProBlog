from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blogs:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Blog(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_PENDING = 'PENDING'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHANGES = 'CHANGES_REQUESTED'
    STATUS_ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CHANGES, 'Changes Requested'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=220)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blogs',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='blogs')
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to='blogs/', blank=True, null=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blogs:blog_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def reading_time(self):
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def increment_views(self):
        Blog.objects.filter(pk=self.pk).update(views=models.F('views') + 1)


class BlogReview(models.Model):
    DECISION_APPROVED = 'APPROVED'
    DECISION_REJECTED = 'REJECTED'
    DECISION_CHANGES = 'CHANGES_REQUESTED'

    DECISION_CHOICES = [
        (DECISION_APPROVED, 'Approved'),
        (DECISION_REJECTED, 'Rejected'),
        (DECISION_CHANGES, 'Changes Requested'),
    ]

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_reviews',
    )
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.blog.title} — {self.decision} by {self.editor}'
