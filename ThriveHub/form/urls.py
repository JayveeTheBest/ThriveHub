from django.urls import path
from . import views


urlpatterns = [
    path('callReports/', views.callReports, name='Reports'),
    path('', views.addCall, name='AddCall'),
    path("save-draft/", views.save_draft, name="save_draft"),
    path('load-draft/', views.load_draft, name='load_draft'),
    path("transcribe/", views.transcribe_audio, name="transcribe"),
    path('callSummary/<int:session_id>', views.summaryPage, name='SummaryPage'),
    path('export', views.exportCallReports, name='Export'),
]