"""
ASGI config for searchOpenAI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # ✅ added
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchOpenAI.settings')

django_asgi_app = get_asgi_application()

# ✅ Serve static files in dev mode
if os.environ.get("DJANGO_DEBUG", "true").lower() == "true":
    django_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})



