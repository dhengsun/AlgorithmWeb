import os
import re
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from .scrapers.luogu import get_luogu_problem
from .scrapers.leetcode import get_leetcode_problem_info
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from algorithm.serializers import CustomTokenObtainPairSerializer
from django.conf import settings
from django.db import transaction
from rest_framework import status
from .models import Question, Solution
from .serializers import QuestionCreateSerializer, SolutionSerializer
from rest_framework import generics
from django.db.models import Q
from algorithm.pagination import QuestionPagination
from algorithm.serializers import *
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.conf import settings
import os
from .pagination import SolutionPagination
from rest_framework.generics import UpdateAPIView
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Question, Solution
import pandas as pd
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # 添加自定义响应数据
            user = User.objects.get(username=request.data['username'])
            response.data.update({
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            })
        
        return response    
    

class QuestionCrawlerView(APIView):
    permission_classes = [IsAuthenticated]
    """题目爬虫接口"""
    
    PLATFORM_MAP = {
        'luogu.com.cn': 'luogu',
        'leetcode.cn': 'leetcode',
        'leetcode.com': 'leetcode'
    }

    LUOGU_DIFFICULTY_MAP = {
        '8': '入门',
        '7': '普及-',
        '6': '普及/提高-',
        '5': '普及+/提高',
        '4': '提高+/省选-',
        '3': '省选/NOI-',
        '2': 'NOI/NOI+',
        '1': 'CTSC'
    }
    
    def __init__(self):
        super().__init__()
        # 读取Excel文件并缓存标签数据
        excel_path = os.path.join(settings.MEDIA_ROOT, 'luogu_tags.xlsx')
        self.df = pd.read_excel(excel_path)
        self.tags_dict = self.df.set_index('id').to_dict('index')
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return self._error_response('缺少URL参数', 400)
            
        platform = self._detect_platform(url)
        if not platform:
            return self._error_response('暂不支持该OJ平台', 400)
        
        crawler_func = {
            'luogu': get_luogu_problem,
            'leetcode': get_leetcode_problem_info
        }[platform]
        
        result = crawler_func(url)
        if 'error' in result:
            return self._error_response(result['error'], 500)
            
        return JsonResponse(self._format_response(platform, result, url))

    def _detect_platform(self, url):
        parsed = urlparse(url)
        for domain in self.PLATFORM_MAP:
            if domain in parsed.netloc:
                return self.PLATFORM_MAP[domain]
        return None

    def _normalize_luogu_tags(self, tag_ids):
        """标准化洛谷标签"""
        normalized_tags = []
        for tag_id in tag_ids:
            tag_info = self.tags_dict.get(int(tag_id))
            if tag_info:
                # 拼接格式：标签类型_标签名
                normalized_tag = f"{tag_info['category']}_{tag_info['name']}"
                normalized_tags.append(normalized_tag)
        return normalized_tags

    def _normalize_difficulty(self, diff, platform):
        """难度标准化"""
        if platform == 'leetcode':
            diff_map = {
                'Easy': '简单',
                'Medium': '中等',
                'Hard': '困难'
            }
            return diff_map.get(diff, diff)
        elif platform == 'luogu':
            return self.LUOGU_DIFFICULTY_MAP.get(str(diff), diff)
        return diff

    def _format_response(self, platform, data, url):
        """更新响应格式"""
        if platform == 'luogu':
            # 标准化洛谷的标签和难度
            algorithm_tags = self._normalize_luogu_tags(data.get('algorithm_tags', []))
            difficulty = self._normalize_difficulty(data.get('difficulty'), platform)
        else:
            # Leetcode保持原有处理方式
            algorithm_tags = data.get('algorithm_tags', [])
            difficulty = self._normalize_difficulty(data.get('difficulty'), platform)

        return {
            'ext_question_id': data.get('external_id'),
            'name': data.get('title'),
            'url': url,
            'oj_platform': platform,
            'algorithm_tags': algorithm_tags,
            'difficulty': difficulty,
            'content': data.get('content')
        }

    def _error_response(self, message, status):
        """错误响应"""
        return JsonResponse(
            {'error': message}, 
            status=status,
            json_dumps_params={'ensure_ascii': False}
        )

    

class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = QuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 检查站外ID是否已存在
                ext_question_id = serializer.validated_data.get('ext_question_id')
                oj_platform = serializer.validated_data['oj_platform']
                if ext_question_id:
                    existing_id = Question.objects.filter(
                        ext_question_id=ext_question_id,
                        oj_platform=oj_platform
                    ).values_list('id', flat=True).first()
                    
                    if existing_id:
                        return Response({
                            'status': 'error',
                            'message': f'该题目已存在，站内ID: {existing_id}'
                        }, status=status.HTTP_409_CONFLICT)

                # 创建Question实例
                question = Question.objects.create(
                    ext_question_id=ext_question_id,
                    name=serializer.validated_data['name'],
                    url=serializer.validated_data['url'],
                    oj_platform=serializer.validated_data['oj_platform'],
                    algorithm_tags=serializer.validated_data.get('algorithm_tags'),
                    difficulty=serializer.validated_data['difficulty']
                )
                
                # 保存描述文件
                self._save_description_file(
                    question=question,
                    content=serializer.validated_data['content']
                )
                
                return Response({
                    'status': 'success',
                    'message': '题目创建成功',
                    'data': {
                        'id': question.id,
                        'name': question.name,
                        'url': question.url,
                        'description': question.description,
                        'oj_platform': question.oj_platform,
                        'difficulty': question.difficulty,
                        'algorithm_tags': question.algorithm_tags
                    }
                }, status=status.HTTP_201_CREATED)
                
        except IOError as e:
            return Response({
                'status': 'error',
                'message': '文件系统操作失败',
                'error_detail': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': '服务器内部错误',
                'error_detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def _save_description_file(self, question, content):
        """文件保存逻辑"""
        try:
            # 确保存储目录存在
            storage_dir = os.path.join(settings.MEDIA_ROOT, 'question_descriptions')
            os.makedirs(storage_dir, exist_ok=True)
            
            # 生成文件路径
            filename = f"{question.id}.md"
            full_path = os.path.join(storage_dir, filename)
            
            # 写入内容
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新模型字段
            question.description = os.path.join('question_descriptions', filename)
            question.save(update_fields=['description'])
            
        except Exception as e:
            # 删除已创建的记录
            if question.pk:
                question.delete()
            raise IOError(f"文件保存失败: {str(e)}")


from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q

from .models import Question
from .serializers import QuestionListSerializer


class QuestionPagination(PageNumberPagination):
    """
    题目列表分页器
    - page: 页码
    - page_size: 每页条数
    """
    page_size = 10  # 默认每页显示10条
    page_size_query_param = 'page_size'  # 允许客户端通过查询参数指定页面大小
    max_page_size = 100  # 最大页面大小


class QuestionListView(generics.ListAPIView):
    """
    获取题目列表的视图，支持各种筛选条件
    - 分页参数通过请求体传递
    - 所有筛选参数通过请求体传递
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QuestionListSerializer
    pagination_class = QuestionPagination
    
    def post(self, request, *args, **kwargs):
        """
        使用POST方法获取题目列表，所有参数通过请求体传递
        """
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        根据请求体中的筛选条件获取题目列表
        """
        # 初始查询集 - 获取所有未删除的题目
        queryset = Question.objects.filter(is_deleted=False)
        
        # 获取分页参数
        page = self.request.query_params.get('page')
        
        # 从请求体获取筛选参数
        if not self.request.data:
            # 如果请求体为空，则返回所有结果（按ID升序）
            return queryset.order_by('id').distinct()
        
        filter_params = self.request.data
        
        # 检查筛选逻辑模式: 'intersection'(交集) 或 'union'(并集)
        filter_mode = filter_params.get('filter_mode', 'intersection')  # 默认为交集
        
        # 处理算法标签筛选
        if algorithm_tags := filter_params.get('algorithm_tags'):
            # 将字符串转换为列表
            algorithm_tag_list = [tag.strip() for tag in algorithm_tags.split(',') if tag.strip()]
            
            # 应用标签筛选逻辑
            if algorithm_tag_list:
                if filter_mode == 'intersection':  # 交集模式 - 每个标签必须都匹配
                    for tag in algorithm_tag_list:
                        # 创建一个查询条件，可以匹配标签本身或者标签的后缀部分
                        tag_q = Q()
                        
                        # 1. 直接匹配标签
                        tag_q |= Q(algorithm_tags__icontains=tag)
                        
                        # 2. 匹配"_标签名"格式
                        tag_q |= Q(algorithm_tags__icontains=f"_{tag}")
                        
                        # 应用本轮标签筛选 - 使用AND逻辑
                        queryset = queryset.filter(tag_q)
                else:  # 并集模式 - 只要匹配任一标签即可
                    # 创建一个OR逻辑的查询
                    tag_q = Q()
                    
                    for tag in algorithm_tag_list:
                        # 1. 直接匹配标签
                        tag_q |= Q(algorithm_tags__icontains=tag)
                        
                        # 2. 匹配"_标签名"格式
                        tag_q |= Q(algorithm_tags__icontains=f"_{tag}")
                    
                    # 应用并集逻辑 - 任一标签条件满足即可（OR逻辑）
                    queryset = queryset.filter(tag_q)
        
        # 难度筛选 - 接收字符串，将其分割为列表
        if difficulties := filter_params.get('difficulties'):
            difficulty_list = [d.strip() for d in difficulties.split(',') if d.strip()]
            
            if difficulty_list:
                queryset = queryset.filter(difficulty__in=difficulty_list)
        
        # OJ平台筛选 - 接收字符串，将其分割为列表
        if platforms := filter_params.get('platforms'):
            platform_list = [p.strip() for p in platforms.split(',') if p.strip()]
            
            if platform_list:
                queryset = queryset.filter(oj_platform__in=platform_list)
        
        # 返回结果并按ID升序排序
        return queryset.order_by('id_num').distinct()

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Question
from .serializers import QuestionListSerializer
from .pagination import QuestionPagination

class QuestionSearchView(generics.ListAPIView):
    """
    题目搜索接口
    - 支持三种搜索方式：精确匹配题目ID、精确匹配站外ID、模糊匹配题目名称
    - 每次只能使用一种搜索方式
    - 分页参数通过URL传递
    - 结果直接按id_num排序
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionListSerializer
    pagination_class = QuestionPagination

    def get_queryset(self):
        """
        根据URL参数获取查询集，并按id_num排序
        """
        # 初始查询集 - 获取所有未删除的题目
        queryset = Question.objects.filter(is_deleted=False)
        
        # 获取搜索参数
        question_id = self.request.query_params.get('id')
        ext_id = self.request.query_params.get('ext_id')
        name = self.request.query_params.get('name')
        
        # 确保每次只使用一种搜索方式
        search_params = [p for p in [question_id, ext_id, name] if p is not None]
        if len(search_params) > 1:
            return queryset.none().order_by('id_num')  # 返回空查询集
        
        # 精确匹配题目ID (如E1, E2等)
        if question_id:
            queryset = queryset.filter(id=question_id)
        
        # 精确匹配站外ID (如P1234, 98等)
        elif ext_id:
            queryset = queryset.filter(ext_question_id=ext_id)
        
        # 模糊匹配题目名称
        elif name:
            queryset = queryset.filter(name__icontains=name)
        
        # 如果没有提供任何搜索参数，返回空查询集
        else:
            return queryset.none().order_by('id_num')
        
        # 直接按照id_num排序
        return queryset.order_by('id_num').distinct()

class QuestionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionDetailSerializer
    queryset = Question.objects.all()
    lookup_field = 'id'  # 匹配E1这类ID

    def get_object(self):
        obj = super().get_object()
        if not obj.description:  # 检查数据库是否存储了文件名
            raise ValidationError("题目描述文件未正确关联")
        return obj

class QuestionDeleteView(APIView):
    """严格处理POST请求的删除接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 从请求体获取ID（非URL参数）
        question_id = request.data.get('id')
        if not question_id:
            return Response(
                {"error": "必须提供 'id' 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 查询未被删除的题目
            question = get_object_or_404(
                Question,
                id=question_id,
                is_deleted=False
            )
            # 执行软删除
            question.is_deleted = True
            question.save()
            return Response(
                {"id": question_id, "is_deleted": True},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SolutionDraftView(APIView):
    permission_classes = [IsAuthenticated]
    """
    题解草稿保存接口（无条件创建新草稿）
    """
    def post(self, request):
        try:
            question_id = request.data.get('question_id')
            content = request.data.get('content')
            language = request.data.get('language', 'c++')  # 默认c++
            
            # 参数校验
            if not all([question_id, content]):
                return Response({
                    'code': 400,
                    'message': '参数不完整'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 无条件创建新草稿（不再检查question_id是否已存在）
            solution = Solution.objects.create(
                question_id=question_id,
                is_draft=True,
                language=language
            )

            # 保持原有的文件存储逻辑
            relative_path = os.path.join('solutions', str(solution.id))
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            os.makedirs(absolute_path, exist_ok=True)
            
            file_path = os.path.join(absolute_path, 'solution.md')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            solution.content.name = os.path.join(relative_path, 'solution.md')
            solution.save()

            return Response({
                'code': 200,
                'message': '草稿保存成功',
                'data': SolutionSerializer(solution).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'保存失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionPublishView(APIView):
    permission_classes = [IsAuthenticated]
    """
    题解发布接口（无条件创建新题解）
    """
    def post(self, request):
        try:
            question_id = request.data.get('question_id')
            content = request.data.get('content')
            language = request.data.get('language', 'c++')  # 默认c++
            
            # 参数校验
            if not all([question_id, content]):
                return Response({
                    'code': 400,
                    'message': '参数不完整'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 无条件创建新题解（不再检查question_id是否已存在）
            solution = Solution.objects.create(
                question_id=question_id,
                is_draft=False,
                language=language
            )

            # 保持原有的文件存储逻辑
            relative_path = os.path.join('solutions', str(solution.id))
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            os.makedirs(absolute_path, exist_ok=True)
            
            file_path = os.path.join(absolute_path, 'solution.md')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            solution.content.name = os.path.join(relative_path, 'solution.md')
            solution.save()

            return Response({
                'code': 200,
                'message': '题解发布成功',
                'data': SolutionSerializer(solution).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'发布失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class SolutionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionListSerializer
    pagination_class = SolutionPagination
    ordering = ['id']  # 默认按 id 升序（可改成 `-id` 降序）

    def get_queryset(self):
        queryset = Solution.objects.filter(is_draft=False, is_deleted=False)
        query_params = self.request.query_params

        # 可选：按题目ID筛选（如果提供了 question_id）
        question_id = query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # 可选：按编程语言筛选（如果提供了 language）
        language = query_params.get('language')
        if language:
            # 支持多语言筛选（例如 ?language=cpp,java）
            languages = language.split(',')
            queryset = queryset.filter(language__in=languages)

        # 可选：按创建时间范围筛选
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 强制按 id 排序（忽略任何传入的排序参数）
        return queryset.order_by('id').distinct()  # 或 '-id' 降序

class SolutionTrashListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionListSerializer
    pagination_class = SolutionPagination
    ordering = ['id']  # 默认按 id 升序（可改成 `-id` 降序）

    def get_queryset(self):
        queryset = Solution.objects.filter(is_draft=False, is_deleted=True)
        query_params = self.request.query_params

        # 可选：按题目ID筛选（如果提供了 question_id）
        question_id = query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # 可选：按编程语言筛选（如果提供了 language）
        language = query_params.get('language')
        if language:
            # 支持多语言筛选（例如 ?language=cpp,java）
            languages = language.split(',')
            queryset = queryset.filter(language__in=languages)

        # 可选：按创建时间范围筛选
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 强制按 id 排序（忽略任何传入的排序参数）
        return queryset.order_by('id').distinct()  # 或 '-id' 降序

class DraftListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionListSerializer
    pagination_class = SolutionPagination
    ordering = ['id']  # 默认按 id 升序（可改成 `-id` 降序）

    def get_queryset(self):
        queryset = Solution.objects.filter(is_draft=True, is_deleted=False)
        query_params = self.request.query_params

        # 可选：按题目ID筛选（如果提供了 question_id）
        question_id = query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # 可选：按编程语言筛选（如果提供了 language）
        language = query_params.get('language')
        if language:
            # 支持多语言筛选（例如 ?language=cpp,java）
            languages = language.split(',')
            queryset = queryset.filter(language__in=languages)

        # 可选：按创建时间范围筛选
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 强制按 id 排序（忽略任何传入的排序参数）
        return queryset.order_by('id').distinct()  # 或 '-id' 降序

class DraftTrashListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionListSerializer
    pagination_class = SolutionPagination
    ordering = ['id']  # 默认按 id 升序（可改成 `-id` 降序）

    def get_queryset(self):
        queryset = Solution.objects.filter(is_draft=True, is_deleted=True)
        query_params = self.request.query_params

        # 可选：按题目ID筛选（如果提供了 question_id）
        question_id = query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # 可选：按编程语言筛选（如果提供了 language）
        language = query_params.get('language')
        if language:
            # 支持多语言筛选（例如 ?language=cpp,java）
            languages = language.split(',')
            queryset = queryset.filter(language__in=languages)

        # 可选：按创建时间范围筛选
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 强制按 id 排序（忽略任何传入的排序参数）
        return queryset.order_by('id').distinct()  # 或 '-id' 降序

class SolutionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionDetailSerializer
    queryset = Solution.objects.filter(is_draft = False)
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        if not obj.content:  # 检查数据库是否存储了文件名
            raise ValidationError("题解内容文件未正确关联")
        return obj
    
class DraftDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionDetailSerializer
    queryset = Solution.objects.filter(is_draft = True)
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        if not obj.content:  # 检查数据库是否存储了文件名
            raise ValidationError("题解内容文件未正确关联")
        return obj



class QuestionCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Question.objects.filter(is_deleted=False).count()
        return Response({
            'count': count,
            'message': 'success'
        })

class SolutionCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Solution.objects.filter(is_draft=False).count()
        return Response({
            'count': count,
            'message': 'success'
        })

class DraftCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Solution.objects.filter(is_draft=True).count()
        return Response({
            'count': count,
            'message': 'success'
        })
    
class SolutionUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionUpdateSerializer
    queryset = Solution.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class DraftUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SolutionUpdateSerializer
    queryset = Solution.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class QuestionUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionUpdateSerializer
    permission_classes = [IsAuthenticated]  # 根据需要设置权限
    lookup_field = 'id'  # 使用 id 字段查找
    lookup_url_kwarg = 'id'  # URL 参数名

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class ActivityView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 获取当前日期
        today = datetime.now()
        
        # 计算12个月前的第一天
        first_day = (today.replace(day=1) - timedelta(days=365)).replace(day=1)
        
        # 查询题目更新记录
        questions = Question.objects.filter(
            updated_at__gte=first_day,
            updated_at__lte=today
        ).annotate(
            date=TruncDate('updated_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 查询草稿更新记录
        drafts = Solution.objects.filter(
            is_draft=True,
            updated_at__gte=first_day,
            updated_at__lte=today
        ).annotate(
            date=TruncDate('updated_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 查询题解更新记录
        solutions = Solution.objects.filter(
            is_draft=False,
            updated_at__gte=first_day,
            updated_at__lte=today
        ).annotate(
            date=TruncDate('updated_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 整合数据
        activity_data = {
            'questions': {str(item['date']): item['count'] for item in questions},
            'drafts': {str(item['date']): item['count'] for item in drafts},
            'solutions': {str(item['date']): item['count'] for item in solutions},
            'time_range': {
                'start': str(first_day.date()),
                'end': str(today.date())
            }
        }
        return Response(activity_data)


class TagInfoView(View):
    permission_classes = [IsAuthenticated]
    def __init__(self):
        super().__init__()
        # 读取Excel文件并缓存数据
        excel_path = os.path.join(settings.MEDIA_ROOT, 'luogu_tags.xlsx')
        self.df = pd.read_excel(excel_path)
        # 将DataFrame转换为以id为索引的字典，方便查询
        self.tags_dict = self.df.set_index('id').to_dict('index')

    def get(self, request, *args, **kwargs):
        try:
            # 获取tag_id参数
            tag_id = request.GET.get('tag_id')
            
            # 验证参数
            if not tag_id:
                return JsonResponse({
                    'code': 400,
                    'message': 'Missing tag_id parameter'
                }, status=400)
            
            # 转换为整数
            tag_id = int(tag_id)
            
            # 查找标签信息
            tag_info = self.tags_dict.get(tag_id)
            
            if tag_info is None:
                return JsonResponse({
                    'code': 404,
                    'message': 'Tag not found'
                }, status=404)
            
            # 返回结果
            return JsonResponse({
                'code': 200,
                'data': {
                    'tag_id': tag_id,
                    'category': tag_info['category'],
                    'name': tag_info['name']
                }
            })
            
        except ValueError:
            return JsonResponse({
                'code': 400,
                'message': 'Invalid tag_id format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': str(e)
            }, status=500)

class TagListView(View):
    permission_classes = [IsAuthenticated]
    def __init__(self):
        super().__init__()
        # 读取Excel文件并缓存数据
        excel_path = os.path.join(settings.MEDIA_ROOT, 'luogu_tags.xlsx')
        self.df = pd.read_excel(excel_path)
        # 预处理数据
        self.process_data()

    def process_data(self):
        # 按category分组，构建层级结构
        grouped = self.df.groupby('category')
        self.tags_tree = {}
        
        for category, group in grouped:
            self.tags_tree[category] = [
                {
                    'tag_id': row['id'],
                    'name': row['name']
                }
                for _, row in group.iterrows()
            ]

    def get(self, request, *args, **kwargs):
        try:
            # 获取可选的format参数，决定返回格式
            format_type = request.GET.get('format', 'tree')
            
            if format_type == 'tree':
                # 返回树形结构
                response_data = {
                    'code': 200,
                    'data': self.tags_tree
                }
            elif format_type == 'flat':
                # 返回扁平结构
                flat_list = [
                    {
                        'tag_id': row['id'],
                        'category': row['category'],
                        'name': row['name']
                    }
                    for _, row in self.df.iterrows()
                ]
                response_data = {
                    'code': 200,
                    'data': flat_list
                }
            else:
                return JsonResponse({
                    'code': 400,
                    'message': 'Invalid format parameter'
                }, status=400)

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': str(e)
            }, status=500)
        
class QuestionTrashListView(generics.ListAPIView):
    """
    获取题目列表的视图，支持各种筛选条件
    - 分页参数通过请求体传递
    - 所有筛选参数通过请求体传递
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QuestionListSerializer
    pagination_class = QuestionPagination
    
    def post(self, request, *args, **kwargs):
        """
        使用POST方法获取题目列表，所有参数通过请求体传递
        """
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        根据请求体中的筛选条件获取题目列表
        """
        # 初始查询集 - 获取所有未删除的题目
        queryset = Question.objects.filter(is_deleted=True)
        
        # 获取分页参数
        page = self.request.query_params.get('page')
        
        # 从请求体获取筛选参数
        if not self.request.data:
            # 如果请求体为空，则返回所有结果（按ID升序）
            return queryset.order_by('id').distinct()
        
        filter_params = self.request.data
        
        # 检查筛选逻辑模式: 'intersection'(交集) 或 'union'(并集)
        filter_mode = filter_params.get('filter_mode', 'intersection')  # 默认为交集
        
        # 处理算法标签筛选
        if algorithm_tags := filter_params.get('algorithm_tags'):
            # 将字符串转换为列表
            algorithm_tag_list = [tag.strip() for tag in algorithm_tags.split(',') if tag.strip()]
            
            # 应用标签筛选逻辑
            if algorithm_tag_list:
                if filter_mode == 'intersection':  # 交集模式 - 每个标签必须都匹配
                    for tag in algorithm_tag_list:
                        # 创建一个查询条件，可以匹配标签本身或者标签的后缀部分
                        tag_q = Q()
                        
                        # 1. 直接匹配标签
                        tag_q |= Q(algorithm_tags__icontains=tag)
                        
                        # 2. 匹配"_标签名"格式
                        tag_q |= Q(algorithm_tags__icontains=f"_{tag}")
                        
                        # 应用本轮标签筛选 - 使用AND逻辑
                        queryset = queryset.filter(tag_q)
                else:  # 并集模式 - 只要匹配任一标签即可
                    # 创建一个OR逻辑的查询
                    tag_q = Q()
                    
                    for tag in algorithm_tag_list:
                        # 1. 直接匹配标签
                        tag_q |= Q(algorithm_tags__icontains=tag)
                        
                        # 2. 匹配"_标签名"格式
                        tag_q |= Q(algorithm_tags__icontains=f"_{tag}")
                    
                    # 应用并集逻辑 - 任一标签条件满足即可（OR逻辑）
                    queryset = queryset.filter(tag_q)
        
        # 难度筛选 - 接收字符串，将其分割为列表
        if difficulties := filter_params.get('difficulties'):
            difficulty_list = [d.strip() for d in difficulties.split(',') if d.strip()]
            
            if difficulty_list:
                queryset = queryset.filter(difficulty__in=difficulty_list)
        
        # OJ平台筛选 - 接收字符串，将其分割为列表
        if platforms := filter_params.get('platforms'):
            platform_list = [p.strip() for p in platforms.split(',') if p.strip()]
            
            if platform_list:
                queryset = queryset.filter(oj_platform__in=platform_list)
        
        # 返回结果并按ID升序排序
        return queryset.order_by('id_num').distinct()

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Question
from .serializers import QuestionListSerializer
from .pagination import QuestionPagination

class QuestionTrashSearchView(generics.ListAPIView):
    """
    题目搜索接口
    - 支持三种搜索方式：精确匹配题目ID、精确匹配站外ID、模糊匹配题目名称
    - 每次只能使用一种搜索方式
    - 分页参数通过URL传递
    - 结果直接按id_num排序
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionListSerializer
    pagination_class = QuestionPagination

    def get_queryset(self):
        """
        根据URL参数获取查询集，并按id_num排序
        """
        # 初始查询集 - 获取所有删除的题目
        queryset = Question.objects.filter(is_deleted=True)
        
        # 获取搜索参数
        question_id = self.request.query_params.get('id')
        ext_id = self.request.query_params.get('ext_id')
        name = self.request.query_params.get('name')
        
        # 确保每次只使用一种搜索方式
        search_params = [p for p in [question_id, ext_id, name] if p is not None]
        if len(search_params) > 1:
            return queryset.none().order_by('id_num')  # 返回空查询集
        
        # 精确匹配题目ID (如E1, E2等)
        if question_id:
            queryset = queryset.filter(id=question_id)
        
        # 精确匹配站外ID (如P1234, 98等)
        elif ext_id:
            queryset = queryset.filter(ext_question_id=ext_id)
        
        # 模糊匹配题目名称
        elif name:
            queryset = queryset.filter(name__icontains=name)
        
        # 如果没有提供任何搜索参数，返回空查询集
        else:
            return queryset.none().order_by('id_num')
        
        # 直接按照id_num排序
        return queryset.order_by('id_num').distinct()
    

class QuestionRestoreView(APIView):
    """严格处理POST请求的恢复接口（与删除接口对称）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 从请求体获取ID（保持与删除接口一致的设计）
        question_id = request.data.get('id')
        if not question_id:
            return Response(
                {"error": "必须提供 'id' 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 查询已被删除的题目（与删除接口相反的条件）
            question = get_object_or_404(
                Question,
                id=question_id,
                is_deleted=True  # 只查找已删除的题目
            )
            # 执行恢复操作（与删除接口相反的操作）
            question.is_deleted = False
            question.save()
            return Response(
                {"id": question_id, "is_restored": True},  # 对称返回字段
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class SolutionSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        软删除接口（通过请求体接收id）
        DELETE /api/solution/delete/
        请求体: {"id": 123}
        """
        try:
            solution_id = request.data.get('id')
            
            if not solution_id:
                return Response({
                    'code': 400,
                    'message': '缺少id参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                solution = Solution.objects.get(pk=solution_id)
                
                # 执行软删除
                solution.is_deleted = True
                solution.save()
                
                # 根据是否是草稿返回不同提示
                message = '草稿删除成功' if solution.is_draft else '题解删除成功'
                
                return Response({
                    'code': 200,
                    'message': message,
                    'data': {
                        'id': solution.id,
                        'is_draft': solution.is_draft,
                        'is_deleted': True
                    }
                }, status=status.HTTP_200_OK)
                
            except Solution.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '未找到指定的题解或草稿'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SolutionRestoreView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        软删除接口（通过请求体接收id）
        DELETE /api/solution/restore/
        请求体: {"id": 123}
        """
        try:
            solution_id = request.data.get('id')
            
            if not solution_id:
                return Response({
                    'code': 400,
                    'message': '缺少id参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                solution = Solution.objects.get(pk=solution_id)
                
                # 执行恢复
                solution.is_deleted = False
                solution.save()
                
                # 根据是否是草稿返回不同提示
                message = '草稿恢复成功' if solution.is_draft else '题解恢复成功'
                
                return Response({
                    'code': 200,
                    'message': message,
                    'data': {
                        'id': solution.id,
                        'is_draft': solution.is_draft,
                        'is_deleted': False
                    }
                }, status=status.HTTP_200_OK)
                
            except Solution.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '未找到指定的题解或草稿'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'恢复失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DraftToSolutionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        发布题解接口（通过请求体接收id）
        POST /api/solution/publish/
        请求体: {"id": 123}
        """
        try:
            solution_id = request.data.get('id')
            
            if not solution_id:
                return Response({
                    'code': 400,
                    'message': '缺少id参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                solution = Solution.objects.get(pk=solution_id)
                
                # 检查是否是草稿
                if not solution.is_draft:
                    return Response({
                        'code': 400,
                        'message': '只能发布草稿状态的题解'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 执行发布（将草稿状态改为false）
                solution.is_draft = False
                solution.save()
                
                return Response({
                    'code': 200,
                    'message': '题解发布成功',
                    'data': {
                        'id': solution.id,
                        'is_draft': False,
                        'is_deleted': solution.is_deleted
                    }
                }, status=status.HTTP_200_OK)
                
            except Solution.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '未找到指定的题解'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'发布失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SolutionToDraftView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        发布题解接口（通过请求体接收id）
        POST /api/draft/pub/
        请求体: {"id": 123}
        """
        try:
            solution_id = request.data.get('id')
            
            if not solution_id:
                return Response({
                    'code': 400,
                    'message': '缺少id参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                solution = Solution.objects.get(pk=solution_id)
                
                # 检查是否是草稿
                if  solution.is_draft:
                    return Response({
                        'code': 400,
                        'message': '已经是草稿无法转换'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 执行发布（将草稿状态改为false）
                solution.is_draft = True
                solution.save()
                
                return Response({
                    'code': 200,
                    'message': '草稿转换成功',
                    'data': {
                        'id': solution.id,
                        'is_draft': True,
                        'is_deleted': solution.is_deleted
                    }
                }, status=status.HTTP_200_OK)
                
            except Solution.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '未找到指定的草稿'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'发布失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
