from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watch', '0008_maintenancetask_after_photo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(
                choices=[
                    ('Submitted', 'Submitted'),
                    ('Under Inspection', 'Under Inspection'),
                    ('Verified', 'Verified'),
                    ('Assigned', 'Assigned'),
                    ('In Progress', 'In Progress'),
                    ('Resolved', 'Resolved'),
                    ('Rejected', 'Rejected'),
                ],
                default='Submitted',
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='maintenancetask',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending Assignment', 'Pending Assignment'),
                    ('Assigned', 'Assigned'),
                    ('In Progress', 'In Progress'),
                    ('Awaiting Review', 'Awaiting Review'),
                    ('Completed', 'Completed'),
                    ('Rework', 'Rework'),
                ],
                default='Pending Assignment',
                max_length=30,
            ),
        ),
    ]
