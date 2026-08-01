from django.urls import path

from .views import LoanDecisionView, LoanReceivedView, LoanRepayView, LoanRequestCreateView, LoanSendView

urlpatterns = [
    path('<str:organization_id>/request/', LoanRequestCreateView.as_view(), name='loan-request'),
    path('<str:loan_id>/decide/', LoanDecisionView.as_view(), name='loan-decide'),
    path('<str:loan_id>/send/', LoanSendView.as_view(), name='loan-send'),
    path('<str:loan_id>/received/', LoanReceivedView.as_view(), name='loan-received'),
    path('<str:loan_id>/repay/', LoanRepayView.as_view(), name='loan-repay'),
]
