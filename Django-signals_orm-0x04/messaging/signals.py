# Django-signals_orm-0x04/messaging/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User

# Task 0: Signal for new message notific
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=f"You have a new message from {instance.sender.username}!"
        )
        print(f"Notification created for {instance.receiver.username} due to new message.")

# Task 1: Signal for logging message edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk: # Check if  instance already exists (i.e., it's an update, not a creation)
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content
                )
                instance.edited = True # Mark message as edited
                print(f"Message {instance.pk} content changed. Old content logged.")
        except Message.DoesNotExist:
            # This can happen if an object is created and saved without a PK being assigned yet.
            # Or if it's a new object being saved for the first time.
            pass

# Task 2: Signal for deleting user-related data
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    # Foreign key CASCADE on Message and Notification models will handle most deletions.
    # However, for MessageHistory, we explicitly delete or ensure CASCADE is set.
    # In our model setup, MessageHistory also has CASCADE on Message, so deleting Message
    # would also delete its history. But if you were to delete a User directly, and not
    # rely on cascading from Messages/Notifications, you'd add:
    # MessageHistory.objects.filter(message__sender=instance).delete()
    # MessageHistory.objects.filter(message__receiver=instance).delete()
    print(f"User {instance.username} deleted. Associated messages, notifications, and message histories are being deleted due to CASCADE.")