# core/signals.py
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .custom_signals import search_completed


@receiver(search_completed)
def send_search_result_via_ws(sender, search_result, **kwargs):
    """
    Sends the search result to the correct WebSocket group for the user.
    """
    if not search_result.user_id: # so we don't send to anonymous users and if there are many users at the same time then we need to make sure we send to the right user
        return  # no user to send to

    channel_layer = get_channel_layer() # this line is for getting the channel layer which means it will allow us to send messages to WebSocket groups
    group_name = f"user_{search_result.user_id}"  # this line is for matching the group name 
    print("📡 Signal fired for user:", search_result.user_id)


    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_search_result",  # must match method in consumer
            "data": {
                "query": search_result.query,
                "results": search_result.results,
                "created_at": search_result.created_at.isoformat(), # isoformat is for converting the datetime to a string format like "2025-01-01T00:00:00"
            },
        }
    )
