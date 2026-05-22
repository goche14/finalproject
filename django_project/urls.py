from django.urls import path, include

urlpatterns = [

    path('api/', include('apps.events.urls')),
    path('api/auth/', include('apps.accounts.urls')),

]