from django.urls import path

from .views import ContributionAcknowledgeView, ContributionCreateView

urlpatterns = [
    path('<str:organization_id>/make/', ContributionCreateView.as_view(), name='contribution-create'),
    path('<str:contribution_id>/acknowledge/', ContributionAcknowledgeView.as_view(), name='contribution-acknowledge'),
]
