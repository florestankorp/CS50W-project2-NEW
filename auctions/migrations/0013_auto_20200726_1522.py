# Generated by Django 3.0.8 on 2020-07-26 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_listing_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('LIT', 'Literature'), ('THR', 'Thriller'), ('COK', 'Cookbook'), ('KID', 'Children'), ('BIO', 'Biography')], max_length=8),
        ),
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(max_length=256),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image_url',
            field=models.URLField(max_length=256),
        ),
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='listing',
            name='starting_bid',
            field=models.PositiveSmallIntegerField(),
        ),
    ]