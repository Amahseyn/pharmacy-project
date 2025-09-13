from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
import json
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Location, Manufacturer, Drug, Pharmacy, PharmacyInventory, User,
    InventorySearchLog
)
from .serializers import (
    LocationSerializer, ManufacturerSerializer, DrugSerializer, PharmacySerializer,
    PharmacyInventoryWriteSerializer, PharmacyInventoryReadSerializer, UserSerializer,
    InventorySearchLogSerializer
)
from .filters import (
    LocationFilter, ManufacturerFilter, DrugFilter, PharmacyFilter,
    PharmacyInventoryFilter, UserFilter, InventorySearchLogFilter
)
from .permissions import IsAdminOrSuperUser


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LocationFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'name', openapi.IN_QUERY,
                description="Filter by location name (e.g., 'Tehran'). Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'type', openapi.IN_QUERY,
                description="Filter by location type (e.g., 'استان', 'شهر'). Exact match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'parent', openapi.IN_QUERY,
                description="Filter by the ID of the parent location.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'parent_name', openapi.IN_QUERY,
                description="Filter by the name of the parent location. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class InventorySearchLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only endpoint to view inventory search logs.
    Accessible only by admins and superusers.
    """
    queryset = InventorySearchLog.objects.all().order_by('-timestamp')
    serializer_class = InventorySearchLogSerializer
    permission_classes = [IsAdminOrSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InventorySearchLogFilter
    



class LogoutView(APIView):
    """
    An endpoint to logout users by blacklisting their refresh token.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Logs out the current user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="The refresh token to be blacklisted.")
            },
        ),
        responses={
            205: "Reset Content - Successful logout.",
            400: "Bad Request - Refresh token is invalid or missing."
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (TokenError, KeyError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ManufacturerFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'name', openapi.IN_QUERY,
                description="Filter by manufacturer name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'country', openapi.IN_QUERY,
                description="Filter by country of origin. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class DrugViewSet(viewsets.ModelViewSet):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    # The filter backend and class still handle the actual filtering logic
    filter_backends = [DjangoFilterBackend]
    filterset_class = DrugFilter

    @swagger_auto_schema(
        # This is where we manually define the parameters for the Swagger UI
        manual_parameters=[
            openapi.Parameter(
                'generic_name',
                openapi.IN_QUERY,
                description="Filter by drug's generic name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'brand_name',
                openapi.IN_QUERY,
                description="Filter by drug's brand name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'manufacturer',
                openapi.IN_QUERY,
                description="Filter by the ID of the manufacturer.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'manufacturer_name',
                openapi.IN_QUERY,
                description="Filter by manufacturer name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'form',
                openapi.IN_QUERY,
                description="Filter by drug form (e.g., 'Tablet', 'Syrup'). Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'irc',
                openapi.IN_QUERY,
                description="Filter by the exact drug registration code (IRC).",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'requires_prescription',
                openapi.IN_QUERY,
                description="Filter for drugs that require a prescription (true/false).",
                type=openapi.TYPE_BOOLEAN
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new drug (with optional image upload).",
        request_body=DrugSerializer
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a drug (with optional image upload).",
        request_body=DrugSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        method='put',
        operation_summary="Upload or replace a drug's image.",
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM,
                description="The image file to upload for the drug.",
                type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={200: DrugSerializer()}
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary="Remove a drug's image.",
        responses={204: 'No Content'}
    )
    @action(detail=True, methods=['put', 'delete'], url_path='image', parser_classes=[MultiPartParser])
    def manage_image(self, request, pk=None):
        """Custom action to upload, update, or delete a drug's image."""
        drug = self.get_object()
        if request.method == 'PUT':
            serializer = self.get_serializer(drug, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            drug.image.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PharmacyFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'name', openapi.IN_QUERY,
                description="Filter by pharmacy name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'location', openapi.IN_QUERY,
                description="Filter by the ID of the pharmacy's location.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'location_name', openapi.IN_QUERY,
                description="Filter by the pharmacy's location name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_24_hours', openapi.IN_QUERY,
                description="Filter for pharmacies that are open 24 hours (true/false).",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'license_number', openapi.IN_QUERY,
                description="Filter by the exact pharmacy license number.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'owner_full_name', openapi.IN_QUERY,
                description="Filter by pharmacy owner's name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'pharmacist_full_name', openapi.IN_QUERY,
                description="Filter by pharmacist's name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new pharmacy (with optional image upload).",
        request_body=PharmacySerializer
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a pharmacy (with optional image upload).",
        request_body=PharmacySerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        method='put',
        operation_summary="Upload or replace a pharmacy's image.",
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM,
                description="The image file to upload for the pharmacy.",
                type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={200: PharmacySerializer()}
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary="Remove a pharmacy's image.",
        responses={204: 'No Content'}
    )
    @action(detail=True, methods=['put', 'delete'], url_path='image', parser_classes=[MultiPartParser])
    def manage_image(self, request, pk=None):
        """Custom action to upload, update, or delete a pharmacy's image."""
        pharmacy = self.get_object()
        if request.method == 'PUT':
            serializer = self.get_serializer(pharmacy, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            pharmacy.image.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

class PharmacyInventoryViewSet(viewsets.ModelViewSet):
    queryset = PharmacyInventory.objects.all()
    # Default serializer for write operations (POST, PUT, PATCH)
    serializer_class = PharmacyInventoryWriteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PharmacyInventoryFilter

    def get_serializer_class(self):
        """
        Use a more detailed serializer for read operations (GET).
        """
        if self.action in ['list', 'retrieve']:
            return PharmacyInventoryReadSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'drug', openapi.IN_QUERY,
                description="Filter by the ID of the drug.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'drug_name', openapi.IN_QUERY,
                description="Filter by the drug's generic name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'pharmacy', openapi.IN_QUERY,
                description="Filter by the ID of the pharmacy.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'pharmacy_name', openapi.IN_QUERY,
                description="Filter by the pharmacy's name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'drug_brand_name', openapi.IN_QUERY,
                description="Filter by the drug's brand name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'drug_form', openapi.IN_QUERY,
                description="Filter by drug form (e.g., 'Tablet'). Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'drug_irc', openapi.IN_QUERY,
                description="Filter by the exact drug registration code (IRC).",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'manufacturer_name', openapi.IN_QUERY,
                description="Filter by the drug's manufacturer name. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'pharmacy_is_24_hours', openapi.IN_QUERY,
                description="Filter for pharmacies that are open 24 hours (true/false).",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'location_district', openapi.IN_QUERY,
                description="Filter by district name (e.g., 'منطقه ۱'). Assumes a 4-level hierarchy.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'location_city', openapi.IN_QUERY,
                description="Filter by city name (e.g., 'تهران').",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'location_county', openapi.IN_QUERY,
                description="Filter by county name (e.g., 'کرج').",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'location_province', openapi.IN_QUERY,
                description="Filter by province name (e.g., 'البرز').",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'has_stock', openapi.IN_QUERY,
                description="Filter for items with quantity greater than 0.",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'batch_number', openapi.IN_QUERY,
                description="Filter by batch number. Case-insensitive, partial match.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'expire_date_after', openapi.IN_QUERY,
                description="Filter for items expiring after this date (YYYY-MM-DD).",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'expire_date_before', openapi.IN_QUERY,
                description="Filter for items expiring before this date (YYYY-MM-DD).",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        # First, get the response from the parent class
        response = super().list(request, *args, **kwargs)

        # Now, log the search query if there are any query parameters
        if request.GET:
            user = request.user if request.user.is_authenticated else None

            # Get the client's real IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Create the search log entry in the new table
            InventorySearchLog.objects.create(
                user=user,
                query_params=json.dumps(request.GET),
                ip_address=ip_address,
            )

        return response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'role', openapi.IN_QUERY,
                description="Filter users by role name (e.g., 'Admin', 'User').",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
