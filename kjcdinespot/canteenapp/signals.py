from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CartItem

@receiver(post_save, sender=CartItem)
def notify_caterer_on_new_order(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "order_notifications",
            {
                "type": "send_notification",
                "message": f"New Order Received! (Order ID: {instance.id})"
            }
        )
