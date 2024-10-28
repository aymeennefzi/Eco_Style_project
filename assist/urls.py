from django.urls import path
from . import views

app_name = 'voice_bot'

urlpatterns = [
    path('start-voice-bot/', views.voice_bot_view, name='start_voice_bot'),
]
