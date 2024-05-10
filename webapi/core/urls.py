from django.urls import re_path
from .views import TestDetailView, TestListView


urlpatterns = [
    re_path(r'test/$', TestListView.as_view()),
    re_path(r'test/(?P<pk>\d+)/$', TestDetailView.as_view()),
]