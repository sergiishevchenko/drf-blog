from django.urls import include, path


app_name = 'users'

urlpatterns = [
    path('', include('users.api.v1.urls')),
]
