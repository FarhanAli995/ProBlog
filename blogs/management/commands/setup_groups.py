from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blogs.models import Blog, Category, Tag, BlogReview
from comments.models import Comment, Report


class Command(BaseCommand):
    help = 'Create Authors, Editors, and Moderators groups with appropriate permissions.'

    def handle(self, *args, **options):
        # ── Authors ───────────────────────────────────────────────────────────
        author_group, _ = Group.objects.get_or_create(name='Authors')
        blog_ct = ContentType.objects.get_for_model(Blog)
        author_perms = Permission.objects.filter(
            content_type=blog_ct,
            codename__in=['add_blog', 'change_blog', 'delete_blog', 'view_blog']
        )
        author_group.permissions.set(author_perms)
        self.stdout.write(self.style.SUCCESS('[OK] Authors group configured'))
        # ── Editors ───────────────────────────────────────────────────────────
        editor_group, _ = Group.objects.get_or_create(name='Editors')
        review_ct = ContentType.objects.get_for_model(BlogReview)
        cat_ct = ContentType.objects.get_for_model(Category)
        tag_ct = ContentType.objects.get_for_model(Tag)
        editor_perms = Permission.objects.filter(
            content_type__in=[blog_ct, review_ct, cat_ct, tag_ct]
        )
        editor_group.permissions.set(editor_perms)
        self.stdout.write(self.style.SUCCESS('[OK] Editors group configured'))

        # ── Moderators ────────────────────────────────────────────────────────
        mod_group, _ = Group.objects.get_or_create(name='Moderators')
        comment_ct = ContentType.objects.get_for_model(Comment)
        report_ct = ContentType.objects.get_for_model(Report)
        mod_perms = Permission.objects.filter(
            content_type__in=[comment_ct, report_ct]
        )
        mod_group.permissions.set(mod_perms)
        self.stdout.write(self.style.SUCCESS('[OK] Moderators group configured'))

        self.stdout.write(self.style.SUCCESS('\nAll groups created successfully!'))
        self.stdout.write('Groups: Authors, Editors, Moderators')
