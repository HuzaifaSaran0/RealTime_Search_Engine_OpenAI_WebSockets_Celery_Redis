from django.urls import re_path
from . import consumers

# WebSocket URLs for the core app
websocket_urlpatterns = [
    re_path(r"^ws/search/(?P<user_id>\d+)/$", consumers.SearchResultConsumer.as_asgi()),
    # this line works in the way that repath matches the websocket URL pattern
    # it captures the user_id from the URL and passes it to the consumer
    # while the ^ sign indicates the start of the string which means it will only match if the URL starts with this pattern
    # while the difference between re_path and path is that re_path allows for more complex regex patterns
]
