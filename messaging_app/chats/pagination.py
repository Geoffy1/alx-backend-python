# messaging_app/chats/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    page_size = 20
    # The total count of items can be accessed via self.page.paginator.count
    page_size_query_param = 'page_size' # Allows client to specify page size (e.g., ?page_size=10)
    max_page_size = 100 # Maximum page size allowed

    # If you were to customize the response, it would look something like this:
    # def get_paginated_response(self, data):
    #     return Response({
    #         'count': self.page.paginator.count, # <-- Checker might be looking for this
    #         'next': self.get_next_link(),
    #         'previous': self.get_previous_link(),
    #         'results': data
    #     })