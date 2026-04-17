from django.urls import path

from .views import DailyReviewAPIView, ProReviewAPIView, WordImportAPIView

urlpatterns = [
    path('review/daily/', DailyReviewAPIView.as_view(), name='daily-review'),
    path('review/pro/', ProReviewAPIView.as_view(), name='pro-review'),
    path('words/import/', WordImportAPIView.as_view(), name='word-import'),
]
