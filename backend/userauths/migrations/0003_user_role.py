from django.db import migrations, models


def mark_existing_instructors(apps, schema_editor):
    User = apps.get_model("userauths", "User")
    Course = apps.get_model("core", "Course")
    instructor_ids = Course.objects.values_list("instructor_id", flat=True).distinct()
    User.objects.filter(id__in=instructor_ids).update(role="instructor")
    User.objects.filter(is_staff=True).update(role="instructor")


class Migration(migrations.Migration):

    dependencies = [
        ("userauths", "0002_alter_profile_full_name_alter_user_full_name"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("student", "Student"), ("instructor", "Instructor")],
                default="student",
                max_length=20,
            ),
        ),
        migrations.RunPython(mark_existing_instructors, migrations.RunPython.noop),
    ]
