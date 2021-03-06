# Generated by Django 2.1.4 on 2019-07-14 11:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('root', models.CharField(max_length=32, null=True, verbose_name='用户')),
                ('ip', models.GenericIPAddressField(null=True, verbose_name='IP')),
                ('port', models.CharField(max_length=32, null=True, verbose_name='端口')),
                ('cmd', models.CharField(max_length=128, null=True, verbose_name='命令')),
                ('user', models.CharField(max_length=32, null=True, verbose_name='操作者')),
                ('ctime', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
            ],
            options={
                'permissions': (('rview_histoy', '查看历史命令'), ('view_cmd', '查看命令行列表'), ('change_cmd', '更新执行命令')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='InstallLogTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=32, null=True, verbose_name='安装服务')),
                ('log_start', models.IntegerField(blank=True, null=True, verbose_name='日志起始位置')),
                ('ctime', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
            ],
            options={
                'permissions': (('view_install_log', '查看安装日志'),),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='InstallYaml',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=32, null=True, verbose_name='安装服务')),
                ('yaml_path', models.CharField(max_length=32, null=True, verbose_name='yaml路径')),
                ('tasks', models.CharField(max_length=32, null=True, verbose_name='执行操作')),
            ],
            options={
                'permissions': (),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='mavenJar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupId', models.CharField(max_length=128, null=True, verbose_name='groupId')),
                ('artifactId', models.CharField(max_length=128, null=True, verbose_name='artifactId')),
                ('version', models.CharField(max_length=32, null=True, verbose_name='version')),
                ('classifier', models.CharField(max_length=128, null=True, verbose_name='classifier')),
                ('deployStatus', models.NullBooleanField(default=True, verbose_name='上传状态')),
                ('ctime', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
                ('user',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL,
                                   verbose_name='操作者')),
            ],
            options={
                'permissions': (('view_mavenJar', '查看上传Jar列表'), ('add_mavenJar', '上传Jar')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='toolsscript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='工具名称')),
                ('tool_script', models.TextField(blank=True, null=True, verbose_name='脚本')),
                ('tool_run_type', models.IntegerField(choices=[(0, 'shell'), (1, 'python'), (2, 'yml')], default=0,
                                                      verbose_name='脚本类型')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='工具说明')),
                ('ctime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('utime', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'permissions': (
                    ('view_toolsScript', '查看脚本工具列表'), ('add_toolsScript', '新增工具脚本'), ('change_toolsScript', '编辑工具脚本'),
                    ('delete_toolsScript', '删除工具脚本')),
                'default_permissions': (),
            },
        ),
    ]
