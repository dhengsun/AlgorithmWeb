from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
import os

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):  # 新增标准方法
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)
    
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('必须设置用户名')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

def question_description_path(instance, filename):
    """生成题目描述的存储路径"""
    return f'question_descriptions/{instance.id}.md'

class Question(models.Model):
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='删除标记',
        help_text='True表示已逻辑删除'
    )

    solution_count = models.PositiveIntegerField(
        default=0,
        verbose_name='题解数量',
        help_text='动态统计关联题解数量'
    )

    OJ_PLATFORM_CHOICES = [
        ('luogu', '洛谷'),
        ('leetcode', 'LeetCode'),
        # 后续可以继续添加其他平台
    ]

    id_num = models.PositiveIntegerField(
        unique=True,
        editable=False,
        verbose_name='数字ID',
        help_text='用于排序的数字部分'
    )

    # 自定义ID字段（主键）
    id = models.CharField(
        primary_key=True,
        max_length=20,
        editable=False,
        verbose_name='题目ID',
        help_text='格式如E1, E2等'
    )
    
    # 题目基本信息
    ext_question_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='外站题目ID',
        help_text='外部平台的题目ID'
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='题目名称'
    )
    url = models.URLField(
        max_length=500,
        blank=False,
        verbose_name='题目链接'
    )
    oj_platform = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='所属OJ平台'
    )
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='题目来源',
        help_text='例如比赛名称等'
    )
    
    # 题目属性
    algorithm_tags = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='算法标签',
        help_text='逗号分隔的算法标签ID，如"1,3,5"'
    )
    difficulty = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='题目难度'
    )
    
    # 题目描述存储
    description = models.FileField(
        upload_to='question_descriptions/',  # 关键修改
        blank=True,
        null=True,
        verbose_name='题目描述路径'
    )
    
    # 时间记录
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目列表'
        ordering = ['id_num']  # 改为按数字ID排序

    def save(self, *args, **kwargs):
        # 只有新建记录时才生成ID
        if not self.id:
            # 获取当前最大数字ID
            last = Question.objects.all().aggregate(models.Max('id_num'))['id_num__max']
            self.id_num = (last or 0) + 1  # 从1开始自增
            self.id = f'E{self.id_num}'  # 生成E前缀的ID
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id} - {self.name}'

    def __str__(self):
        return f'{self.id} - {self.name}'
    

class Solution(models.Model):
    LANGUAGE_CHOICES = [
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('go', 'Go'),
        ('other', '其他')
    ]

    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='solutions',
        verbose_name='关联题目'
    )
    content = models.FileField(
        upload_to='question_solutions/',
        null=True,
        blank=True,
        verbose_name='题解文件'
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='other',
        verbose_name='编程语言'
    )
    is_draft = models.BooleanField(
        default=True,
        verbose_name='是否为草稿'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否已删除'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'solution'
        ordering = ['-updated_at']
        verbose_name = '题解'
        verbose_name_plural = '题解'

    def __str__(self):
        return f"Solution {self.id} for Question {self.question_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)