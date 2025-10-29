from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'account'

router = DefaultRouter()
router.register(r'users', views.UserAuthenticationViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/update/', views.UpdateProfileAPIView.as_view(), name='update-profile'),
    path('diary/<int:diary_id>/', views.GetMyDiaryAPIView.as_view(), name='update-profile'),
]