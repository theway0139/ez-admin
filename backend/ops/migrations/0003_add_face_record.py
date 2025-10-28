# Generated manually for Face Record model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0002_dog_camera_alarmevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='姓名')),
                ('employee_id', models.CharField(max_length=50, unique=True, verbose_name='人员ID')),
                ('department', models.CharField(blank=True, max_length=100, null=True, verbose_name='部门')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='faces/', verbose_name='人脸照片')),
                ('avatar_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='人脸照片路径')),
                ('status', models.CharField(choices=[('active', '已激活'), ('inactive', '未激活')], default='active', max_length=20, verbose_name='状态')),
                ('face_encoding', models.TextField(blank=True, null=True, verbose_name='人脸特征编码')),
                ('description', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '人脸记录',
                'verbose_name_plural': '人脸记录',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='facerecord',
            index=models.Index(fields=['employee_id'], name='ops_facerec_employe_idx'),
        ),
        migrations.AddIndex(
            model_name='facerecord',
            index=models.Index(fields=['status'], name='ops_facerec_status_idx'),
        ),
        migrations.AddIndex(
            model_name='facerecord',
            index=models.Index(fields=['-created_at'], name='ops_facerec_created_idx'),
        ),
    ]

