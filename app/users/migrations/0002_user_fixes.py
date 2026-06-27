# Generated to fix the CustomUser model: drop the misspelled ``fist_name``
# column, restore the proper ``objects`` manager and remove the stray
# ``username`` manager attribute that shadowed AbstractUser's username field.

from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # The initial migration created a column called ``fist_name`` (typo) that
        # nothing in the code ever used; ``first_name`` comes from AbstractUser.
        migrations.RemoveField(
            model_name='customuser',
            name='fist_name',
        ),
        # Tighten the inherited name fields to match the forms / manager signature.
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        # 0001 registered managers as [('username', Manager), ('objects', UserManager)].
        # ``username`` was never a manager — it was a typo that overwrote the field.
        # Restore a single ``objects`` CustomUserManager so CustomUser.objects works.
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
    ]
