# from django.dispatch import receiver
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from .signals import search_completed
# from .serializers import SearchResultSerializer  # If you have DRF serializer

# @receiver(search_completed)
# def broadcast_search_result(sender, search_result, **kwargs):
#     # if not search_result.user_id:
#     #     return  # Skip if there's no user
#     channel_layer = get_channel_layer()
#     group_name = f"user_{search_result.user_id}"

#     data = {
#         "query": search_result.query,
#         "results": search_result.results,
#         "created_at": search_result.created_at.isoformat(),
#     }

#     async_to_sync(channel_layer.group_send)(
#         group_name,
#         {   
#             "type": "send_search_result",
#             "data": data
#         }
#     )
