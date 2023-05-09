from django.contrib import admin
from .models import FriendRequest, Friend

#регистрируем модели для админ-панели
admin.site.register(FriendRequest)
admin.site.register(Friend)

