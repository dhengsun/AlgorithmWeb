from rest_framework.pagination import PageNumberPagination

# 已有的题目分页器
class QuestionPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

# 题解分页器
class SolutionPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
