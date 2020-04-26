from django.db import migrations
from monitoring.models import Host


def fill_table(*args, **kwargs):
    for i in range(1, 11):
        Host.objects.create(hostname="Host{0}".format(str(i)))


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_table)
    ]
