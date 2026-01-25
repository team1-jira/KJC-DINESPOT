# from django.urls import path
# from canteenapp.consumers import NotificationConsumer

# websocket_urlpatterns = [
#     path('ws/notifications/', NotificationConsumer.as_asgi()),  # ✅ Fix WebSocket URL
# ]
from django.urls import path
from .consumers import OrderNotificationConsumer

websocket_urlpatterns = [
    path("ws/canteen/<int:canteen_id>/", OrderNotificationConsumer.as_asgi()),
]

