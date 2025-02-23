from django.urls import path
from . import views


urlpatterns = [
    path('callReports/', views.callReports, name='Reports'),
    path('', views.addCall, name='AddCall'),
    path('callSummary/<int:session_id>', views.summaryPage, name='SummaryPage'),
    path('export', views.exportCallReports, name='Export'),
]