from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing


"""  The AuthMiddlewareStack class provided by Channels
 supports standard Django authentication, where the user details are stored in
the session. """


application = ProtocolTypeRouter({
 'websocket': AuthMiddlewareStack(
 	URLRouter(chat.routing.websocket_urlpatterns)
    ),
})