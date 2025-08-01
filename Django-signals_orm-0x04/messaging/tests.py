# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

class MessageSignalTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password123')

    def test_new_message_creates_notification(self):
        """
        Tests that a new message triggers a notification for the receiver.
        """
        self.assertEqual(Notification.objects.count(), 0)
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello Bob!")
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertIn("You have a new message from alice!", notification.content)

    def test_message_edit_logs_history(self):
        """
        Tests that editing a message creates a MessageHistory entry.
        """
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Original content")
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(message.edited)

        # Edit the message
        message.content = "Updated content"
        message.save()

        self.assertEqual(MessageHistory.objects.count(), 1)
        history_entry = MessageHistory.objects.first()
        self.assertEqual(history_entry.message, message)
        self.assertEqual(history_entry.old_content, "Original content")

        # Refresh the message instance to get the updated 'edited' field
        message.refresh_from_db()
        self.assertTrue(message.edited)

    def test_user_deletion_cleans_up_data(self):
        """
        Tests that deleting a user also deletes their related messages, notifications,
        and message histories due to CASCADE.
        """
        # Messages will automatically create notifications via the signal
        message1 = Message.objects.create(sender=self.user1, receiver=self.user2, content="Msg 1")
        message2 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Msg 2")

        # The signal for editing logs the history
        message1.content = "Msg 1 edited"
        message1.save()

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 2)
        # Now there should be exactly 2 notifications from the two message creations
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.count(), 1)

        # Delete user1
        user1_id = self.user1.id
        self.user1.delete()

        self.assertEqual(User.objects.count(), 1)
        # The CASCADE on foreign keys should have deleted all related objects
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(MessageHistory.objects.count(), 0)

"""  def test_user_deletion_cleans_up_data(self):
        
        message1 = Message.objects.create(sender=self.user1, receiver=self.user2, content="Msg 1")
        message2 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Msg 2")
        # Triggering a save on message1 to create history for Task 1 test later
        message1.content = "Msg 1 edited"
        message1.save()

        # Create notifications
        Notification.objects.create(user=self.user1, message=message2, content="Notif 1")
        Notification.objects.create(user=self.user2, message=message1, content="Notif 2")

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.count(), 1)

        # Delete user1
        user1_id = self.user1.id
        self.user1.delete()

        self.assertEqual(User.objects.count(), 1) # Only user2 remains
        self.assertEqual(Message.objects.filter(sender=user1_id).count(), 0) # messages sent by user1
        self.assertEqual(Message.objects.filter(receiver=user1_id).count(), 0) # messages received by user1
        self.assertEqual(Notification.objects.filter(user=user1_id).count(), 0) # notifications for user1
        # The history associated with message1 should also be gone because message1 is gone
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0) # All messages should be gone
        self.assertEqual(Notification.objects.count(), 0) # All notifications should be gone """