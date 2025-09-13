from rest_framework import serializers
from .models import (
    Role, User, Location, Manufacturer, Drug, Pharmacy, PharmacyInventory,
    InventorySearchLog
)

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for the Role model."""
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the custom User model."""
    # Use SlugRelatedField to represent the role by its name.
    role = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Role.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = User
        # Include fields from AbstractUser and custom fields.
        fields = [
            'id', 'contact_number', 'password', 'full_name', 'role',
            'is_active', 'date_joined', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['date_joined', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
        }

    def create(self, validated_data):
        """Handle password hashing on user creation."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Handle password hashing on user update."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for the Location model with nested children."""
    # Recursively serialize child locations.
    children = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'type', 'parent', 'children']

    def get_children(self, obj):
        """Return serialized children for a location."""
        return LocationSerializer(obj.children.all(), many=True, context=self.context).data

    def validate(self, data):
        """
        Ensures that the parent-child relationship follows the defined hierarchy:
        استان -> شهرستان -> شهر -> منطقه
        """
        # On updates, `self.instance` has old values, `data` has new ones.
        # We get the final state of `type` and `parent` for validation.
        loc_type = data.get('type', getattr(self.instance, 'type', None))
        parent = data.get('parent', getattr(self.instance, 'parent', None))

        # Define the valid parent type for each child type.
        # (فرزند: والد)
        hierarchy = {
            'منطقه': 'شهر',
            'شهر': 'شهرستان',
            'شهرستان': 'استان',
        }

        # Rule 1: A Province ('استان') cannot have a parent.
        if loc_type == 'استان':
            if parent is not None:
                raise serializers.ValidationError({"parent": "یک استان (Province) نمی‌تواند والد داشته باشد."})
            return data

        # Rule 2: Non-province locations must have a parent.
        if parent is None:
            raise serializers.ValidationError({"parent": f"یک '{loc_type}' باید یک والد داشته باشد."})

        # Rule 3: The parent must be of the correct hierarchical type.
        required_parent_type = hierarchy.get(loc_type)
        if parent.type != required_parent_type:
            raise serializers.ValidationError({
                "parent": f"والد یک '{loc_type}' باید از نوع '{required_parent_type}' باشد، اما والد ارائه شده از نوع '{parent.type}' است."
            })

        return data

class ManufacturerSerializer(serializers.ModelSerializer):
    """Serializer for the Manufacturer model."""
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'country']

class DrugSerializer(serializers.ModelSerializer):
    """Serializer for the Drug model."""
    # Display manufacturer name for readability on GET requests.
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Drug
        fields = [
            'id', 'generic_name', 'brand_name', 'irc', 'dosage', 'form',
            'manufacturer', 'manufacturer_name', 'requires_prescription', 'image'
        ]
        # 'manufacturer' is write-only, 'manufacturer_name' is read-only.
        extra_kwargs = {'manufacturer': {'write_only': True}}

class PharmacySerializer(serializers.ModelSerializer):
    """Serializer for the Pharmacy model."""
    # Display location name for readability on GET requests.
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = Pharmacy
        fields = [
            'id', 'name', 'license_number', 'owner_full_name', 'owner_phone_number',
            'pharmacist_full_name', 'pharmacist_phone_number', 'phone_number',
            'is_24_hours', 'address', 'location', 'location_name', 'image'
        ]
        # 'location' is write-only, 'location_name' is read-only.
        extra_kwargs = {'location': {'write_only': True}}

class PharmacyInventoryWriteSerializer(serializers.ModelSerializer):
    """Serializer for WRITE operations on PharmacyInventory (POST, PUT, PATCH)."""
    class Meta:
        model = PharmacyInventory
        fields = [
            'id', 'drug', 'pharmacy', 'batch_number',
            'expire_date', 'quantity', 'price', 'last_updated'
        ]
        read_only_fields = ('last_updated',)

class InventorySearchLogSerializer(serializers.ModelSerializer):
    """Serializer for the InventorySearchLog model."""
    # Display user's contact number for better readability
    user = serializers.StringRelatedField()

    class Meta:
        model = InventorySearchLog
        fields = ['id', 'user', 'query_params', 'ip_address', 'timestamp']
        read_only_fields = fields

class PharmacyInventoryReadSerializer(serializers.ModelSerializer):
    """Serializer for READ operations on PharmacyInventory (GET list/detail)."""
    # Use nested serializers for detailed representation.
    drug = DrugSerializer(read_only=True)
    pharmacy = PharmacySerializer(read_only=True)

    class Meta:
        model = PharmacyInventory
        fields = [
            'id', 'drug', 'pharmacy', 'batch_number',
            'expire_date', 'quantity', 'price', 'last_updated'
        ]