# Generated by Django 2.1.2 on 2018-10-28 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20181028_1332'),
    ]

    operations = [
        migrations.RenameField(
            model_name='split',
            old_name='account',
            new_name='target_account',
        ),
        migrations.AddField(
            model_name='account',
            name='abstract',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='commodity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Commodity'),
        ),
        migrations.AlterField(
            model_name='account',
            name='commodity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounting.Commodity'),
        ),
        migrations.AlterField(
            model_name='split',
            name='commodity_rate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='splits', to='accounting.CommodityRate'),
        ),
    ]