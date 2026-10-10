from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('watch', '0009_review_workflow_statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='admin_reply',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='replied_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='replied_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='feedback_replies',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
