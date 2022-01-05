# Generated by Django 3.2.10 on 2022-01-03 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20220103_1440'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='recipe',
            name='link',
            field=models.URLField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='time_minutes',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]