
from django.urls import path
from .views import GetRandomChatView, StoreResponseView

urlpatterns = [
    path('store-response/', StoreResponseView.as_view(), name='store-response'),
    path('get-random-chat/', GetRandomChatView.as_view(), name='get-random-chat'),

]
