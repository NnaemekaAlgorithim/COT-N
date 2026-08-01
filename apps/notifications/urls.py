from django.urls import path

from .views import (
    DeviceTokenRegisterView,
    DeviceTokenUnregisterView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('devices/register/', DeviceTokenRegisterView.as_view(), name='device-register'),
    path('devices/unregister/', DeviceTokenUnregisterView.as_view(), name='device-unregister'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('<str:notification_id>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
]
