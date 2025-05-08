from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tutor.urls')),                        # app views (landing, predict, dashboard)
    path('accounts/', include('django.contrib.auth.urls')), # login/logout
]
