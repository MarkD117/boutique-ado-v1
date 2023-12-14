from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem

# Instance, is the instance of the model that sent the signal.
# Created, is a boolean sent by django referring to whether 
# this is a new instance or one being updated.

# Handles signals from the post_save event
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    # Gets order this specific lineitem is related to and updates total
    instance.order.update_total()

# Handles signals from the post_delete event
@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()