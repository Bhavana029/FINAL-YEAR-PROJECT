from django.urls import path
from .views import login_view, register_view, logout_view, home_view, working_view

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    
      path('working/', working_view, name='working'), 
    path('register/', register_view, name='register'),
     path('home/', home_view, name='home'), 
    path('logout/', logout_view, name='logout'),
]
