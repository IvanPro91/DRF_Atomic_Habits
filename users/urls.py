from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import CreateProductPrice, PayViewSet, UserCreateAPIView, UserViewSet, user_subscribe_course

app_name = UsersConfig.name
router = DefaultRouter()
router.register(r"payments", PayViewSet)
router.register(r"", UserViewSet)

urlpatterns = [
    path("create_product/", CreateProductPrice.as_view(), name="create_product"),
    path("subscribe/", user_subscribe_course, name="subscribe"),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
]

urlpatterns += router.urls
