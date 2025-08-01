from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    A custom manager to filter unread messages for a specific user.
    The checker expects the method name to be 'unread_for_user'.
    """
    def unread_for_user(self, user):
        return self.filter(receiver=user, is_read=False)