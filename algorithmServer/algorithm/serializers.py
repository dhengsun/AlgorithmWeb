from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Question, User, Solution
import logging
import os
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'id': self.user.id,
            'username': self.user.username
        })
        return data

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class QuestionSerializer(serializers.ModelSerializer):
    algorithm_tags = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        allow_empty=True,
        required=False,
        help_text='算法标签ID列表 (如 [1,3,5])'
    )
    solution_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'description')
        extra_kwargs = {
            'url': {'required': True},
            'oj_platform': {'allow_blank': True},
            'ext_question_id': {'allow_blank': True}
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.algorithm_tags:
            rep['algorithm_tags'] = [int(tag) for tag in instance.algorithm_tags.split(',')]
        else:
            rep['algorithm_tags'] = []
        # 添加 solution_count
        rep['solution_count'] = getattr(instance, 'solution_count', 0)
        return rep

    def validate_algorithm_tags(self, value):
        processed_tags = sorted(list(set(value)))
        if any(tag < 0 for tag in processed_tags):
            raise serializers.ValidationError("标签ID不能为负数")
        return processed_tags

    def validate_url(self, value):
        if not value.startswith(('https://', 'http://')):
            raise serializers.ValidationError("URL必须以http://或https://开头")
        if len(value) > 500:
            raise serializers.ValidationError("URL长度不能超过500字符")
        return value

    def create(self, validated_data):
        tags = validated_data.pop('algorithm_tags', [])
        validated_data['algorithm_tags'] = ','.join(map(str, tags)) if tags else None
        return Question.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'algorithm_tags' in validated_data:
            tags = validated_data.pop('algorithm_tags')
            instance.algorithm_tags = ','.join(map(str, tags)) if tags else None
        
        for key, value in validated_data.items():
            setattr(instance, key, value)
            
        instance.save()
        return instance

class QuestionCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(write_only=True, required=True)
    algorithm_tags = serializers.ListField(
        child=serializers.CharField(),  # 改为CharField接收字符串标签
        required=False,
        allow_empty=True
    )
    solution_count = serializers.IntegerField(read_only=True, default=0)
    is_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Question
        fields = [
            'ext_question_id',
            'name',
            'url',
            'oj_platform',
            'algorithm_tags',
            'difficulty',
            'content',
            'solution_count',
            'is_deleted'
        ]

    def validate_algorithm_tags(self, value):
        """验证并转换标签列表"""
        if not value:
            return None
        
        # 直接将字符串列表转换为逗号分隔的字符串
        return ','.join(str(tag).strip() for tag in value if tag)

class QuestionListSerializer(serializers.ModelSerializer):
    algorithm_tags = serializers.SerializerMethodField()
    solution_count = serializers.IntegerField(read_only=True, default=0)
    is_deleted = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id',
            'name',
            'oj_platform',
            'ext_question_id',
            'algorithm_tags',
            'difficulty',
            'solution_count',
            'is_deleted'
        ]

    def get_algorithm_tags(self, obj):
        return [tag for tag in obj.algorithm_tags.split(',')] if obj.algorithm_tags else []

class QuestionDetailSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    algorithm_tags = serializers.SerializerMethodField()
    solution_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Question
        fields = [
            'id', 
            'ext_question_id', 
            'name', 
            'oj_platform',
            'difficulty',
            'algorithm_tags',
            'content',
            'created_at',
            'solution_count',
            'is_deleted',
            'updated_at'
        ]

    def get_content(self, obj):
        if not obj.description:
            logger.error(f"题目 {obj.id} 未关联描述文件")
            return None

        try:
            logger.debug(f"尝试读取文件：{obj.description.path}")
            with open(obj.description.path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"成功读取 {obj.id} 的内容")
                return content
        except Exception as e:
            logger.error(f"文件读取失败：{str(e)}", exc_info=True)
            return None

    def get_algorithm_tags(self, obj):
        return obj.algorithm_tags.split(',') if obj.algorithm_tags else []
    

class SolutionSerializer(serializers.ModelSerializer):
    file_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Solution
        fields = ['id', 'question_id', 'language', 'file_path', 
                 'is_draft', 'is_deleted', 'created_at', 'updated_at']
    
    def get_file_path(self, obj):
        return os.path.join(settings.MEDIA_ROOT, 'question_solutions', f'{obj.id}.md')


class SolutionListSerializer(serializers.ModelSerializer):
    content_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Solution
        fields = [
            'id',
            'question_id',
            'content',
            'content_text',
            'language',
            'is_draft',
            'is_deleted',
            'created_at',
            'updated_at'
        ]

    def get_content_text(self, obj):
        if obj.content and os.path.exists(obj.content.path):
            try:
                with open(obj.content.path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return ""
        return ""

class SolutionDetailSerializer(serializers.ModelSerializer):
    content_text = serializers.SerializerMethodField()

    class Meta:
        model = Solution
        fields = [
            'id',
            'question_id',
            'content',
            'content_text',
            'language',
            'is_draft',
            'is_deleted',
            'created_at',
            'updated_at'
        ]

    def get_content_text(self, obj):
        if not obj.content:
            logger.error(f"Solution {obj.id} has no associated content file")
            return None

        try:
            logger.debug(f"Attempting to read file: {obj.content.path}")
            with open(obj.content.path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Successfully read content for solution {obj.id}")
                return content
        except Exception as e:
            logger.error(f"File read failed: {str(e)}", exc_info=True)
            return None


class SolutionUpdateSerializer(serializers.ModelSerializer):
    content_text = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = Solution
        fields = [
            'question_id', 
            'content', 
            'language', 
            'content_text',
            'is_draft',
            'is_deleted'
        ]
        extra_kwargs = {
            'question_id': {'required': False},
            'language': {'required': False},
            'content': {'read_only': True},
            'is_deleted': {'read_only': True}  # Typically you don't want to allow direct updates to is_deleted
        }

    def update(self, instance, validated_data):
        if 'content_text' in validated_data:
            try:
                with open(instance.content.path, 'w', encoding='utf-8') as f:
                    f.write(validated_data.pop('content_text'))
            except IOError as e:
                raise serializers.ValidationError(f"Failed to write file: {str(e)}")
        
        return super().update(instance, validated_data)

class QuestionUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(write_only=True, required=False)
    algorithm_tags = serializers.ListField(
        child=serializers.CharField(),  # 接收字符串标签
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Question
        fields = ['ext_question_id', 'name', 'url', 'oj_platform', 
                 'algorithm_tags', 'difficulty', 'content']
        extra_kwargs = {
            'ext_question_id': {'required': False},
            'name': {'required': False},
            'url': {'required': False},
            'oj_platform': {'required': False},
            'difficulty': {'required': False},
        }

    def validate_algorithm_tags(self, value):
        """验证标签格式并去重"""
        if not all(isinstance(tag, str) and tag.startswith('Algorithm_') for tag in value):
            raise serializers.ValidationError("标签格式必须为'Algorithm_xxx'")
        return sorted(list(set(value)))  # 去重+排序

    def update(self, instance, validated_data):
        # 处理content
        if 'content' in validated_data:
            try:
                with open(instance.description.path, 'w', encoding='utf-8') as f:
                    f.write(validated_data.pop('content'))
            except IOError as e:
                raise serializers.ValidationError(f"文件写入失败: {str(e)}")
        
        # 处理algorithm_tags（字符串数组转逗号分隔）
        if 'algorithm_tags' in validated_data:
            tags = validated_data.pop('algorithm_tags')
            instance.algorithm_tags = ','.join(tags) if tags else None
        
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance