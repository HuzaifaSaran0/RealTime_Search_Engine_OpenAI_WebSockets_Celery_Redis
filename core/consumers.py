import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SearchResultConsumer(AsyncWebsocketConsumer): # this line is defining a WebSocket consumer for search results and AsyncWebsocketConsumer is a built-in Django Channels class for handling WebSocket connections
    async def connect(self): # this method is called when the WebSocket is handshaking as part of the connection process and the handshaking means establishing a connection between the client and the server, and handshaking contains these steps, 
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]  # this line captures the user_id from the URL and passes it to the consumer, and consumer here is the instance of SearchResultConsumer
        self.room_group_name = f"user_{self.user_id}"  # this line creates a unique room group name for the user where group means a collection of WebSocket connections that can receive messages simultaneously and the name self.room_group_name is used to identify the group where self. is must to write while room_group_name is just a variable name which could be anything

        # Join the user's group
        await self.channel_layer.group_add( # here await is used to ensure that the group_add operation is completed before moving on
            self.room_group_name,   # this room_group_name is the variable name
            self.channel_name       # and this channel_name is actually a unique identifier for the WebSocket connection
        )

        await self.accept() 

    async def disconnect(self, close_code):
        # Leave the group when socket closes
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_search_result(self, event):
        """
        This method will be called when group_send() sends an event
        with type="send_search_result"
        """
        await self.send(text_data=json.dumps(event["data"])) # this line sends the search result data to the WebSocket client, and text_data is the data that will be sent to the client, and json.dumps() is used to convert the Python dictionary to a JSON string
