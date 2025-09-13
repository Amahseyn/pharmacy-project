from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    LocationViewSet, ManufacturerViewSet, DrugViewSet, PharmacyViewSet,
    PharmacyInventoryViewSet, UserViewSet, LogoutView, InventorySearchLogViewSet
)

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'drugs', DrugViewSet)
router.register(r'pharmacies', PharmacyViewSet)
router.register(r'inventory', PharmacyInventoryViewSet)
router.register(r'users', UserViewSet)
router.register(r'inventory-search-logs', InventorySearchLogViewSet, basename='inventory-search-log')


urlpatterns = [
    path('', include(router.urls)),
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]