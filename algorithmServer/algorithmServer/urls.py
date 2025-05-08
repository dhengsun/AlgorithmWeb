"""
URL configuration for algorithmServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from algorithm.views import *
urlpatterns = [
    path("admin/", admin.site.urls),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('api/questions/extract/', QuestionCrawlerView.as_view(), name='QuestionExtract'),
    path('api/questions/create/', QuestionCreateView.as_view(), name='question-create'),
    path('api/questions/', QuestionListView.as_view(), name='question-list'),
    path('api/questions/search/',QuestionSearchView.as_view(), name='search-question'),
    path('api/questions/trash/', QuestionTrashListView.as_view(), name='questionTrash-list'),
    path('api/questions/trash/search/',QuestionTrashSearchView.as_view(), name='search-questionTrash'),
    path('questions/<str:id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('api/questions/delete/', QuestionDeleteView.as_view(), name='question-delete'),
    path('api/questions/restore/', QuestionRestoreView.as_view(), name='questionTrash-restore'),
    path('api/solution/draft/', SolutionDraftView.as_view(), name='solution-draft'),
    path('api/solution/create/', SolutionPublishView.as_view(), name='solution-publish'),
    path('api/solutions/', SolutionListView.as_view(), name='solution-list'),
    path('api/solutions/trash/', SolutionTrashListView.as_view(), name='solutionTrash-list'),
    path('api/drafts/', DraftListView.as_view(), name='draft-list'),
    path('api/drafts/trash/', DraftTrashListView.as_view(), name='draftTrash-list'),
    path('solutions/<str:id>/', SolutionDetailView.as_view(), name='solution-detail'),
    path('drafts/<str:id>/', DraftDetailView.as_view(), name='draft-detail'),
    path('api/questions/count/', QuestionCountView.as_view(), name='question-count'),
    path('api/solutions/count/', SolutionCountView.as_view(), name='solution-count'),
    path('api/drafts/count/', DraftCountView.as_view(), name='draft-count'),
    path('solutions/<str:id>/update/', SolutionUpdateView.as_view(), name='solution-update'),
    path('drafts/<str:id>/update/', DraftUpdateView.as_view(), name='draft-update'),
    path('questions/<str:id>/update/', QuestionUpdateView.as_view(), name='question-update'),
    path('api/solution/delete/', SolutionSoftDeleteView.as_view(), name='solution/draft-delete'),
    path('api/solution/restore/', SolutionRestoreView.as_view(), name='solution/draft-restore'),
    path('api/solution/pub/', DraftToSolutionView.as_view(), name='draft-to-solution'),
    path('api/draft/pub/', SolutionToDraftView.as_view(), name='solution-to-draft'),
    path('api/activity/', ActivityView.as_view(), name='activity'),
    path('api/tag/', TagInfoView.as_view(), name='luogu_tag'),
    path('api/tags/', TagListView.as_view(), name='luogu-tags')
]


