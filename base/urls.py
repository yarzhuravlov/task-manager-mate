from django.urls import path

from base.views import HomeTemplateView


urlpatterns = [path("", HomeTemplateView.as_view(), name="index")]

app_name = "base"
