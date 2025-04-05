from django.urls import path
from . import views


urlpatterns = [
    path('callReports/', views.callReports, name='Reports'),
    path('', views.addCall, name='AddCall'),
    path("save-draft/", views.save_draft, name="save_draft"),
    path('api/referrals/', views.get_referrals, name='get_referrals'),
    path('load-draft/', views.load_draft, name='load_draft'),
    path("transcribe/", views.transcribe_audio, name="transcribe"),
    path('forward_transcript/', views.forward_transcript, name='forward_transcript'),
    path('generate_summary_from_transcript/', views.generate_summary_from_transcript, name='generate_summary_from_transcript'),
    path('callSummary/<int:session_id>', views.summaryPage, name='SummaryPage'),
    path('export', views.exportCallReports, name='Export'),
]