# Generated by Django 2.1.4 on 2019-07-14 11:17

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(max_length=40, unique=True, verbose_name='用户名')),
                ('first_name', models.CharField(max_length=40, null=True, verbose_name='姓')),
                ('last_name', models.CharField(max_length=40, null=True, verbose_name='名')),
                ('email', models.EmailField(max_length=100, null=True, verbose_name='邮箱')),
                ('mobile', models.CharField(max_length=30, null=True, validators=[
                    django.core.validators.RegexValidator('^[0-9+()-]+$', 'Enter a valid mobile number.', 'invalid')],
                                            verbose_name='手机')),
                ('fullname', models.CharField(max_length=64, null=True, verbose_name='中文姓名')),
                ('is_active', models.BooleanField(default=False, verbose_name='激活')),
                ('is_staff', models.BooleanField(default=False, verbose_name='管理员')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='超级管理员')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最近登录时间')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True,
                                                  help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user', to='auth.Group',
                                                  verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user',
                                                            to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'permissions': (
                    ('view_user', '查看用户'), ('add_user', '添加用户'), ('edit_user', '编辑用户'), ('del_user', '删除用户')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'permissions': (('view_contact', '获取邮件组列表'), ('add_contact', '添加邮件组'), ('edit_contact', '编辑邮件组'),
                                ('del_contact', '删除邮件组')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'permissions': (
                    ('view_project', '获取项目列表'), ('add_project', '添加项目'), ('edit_project', '编辑项目'),
                    ('del_project', '删除项目')),
                'default_permissions': (),
            },
        ),
    ]