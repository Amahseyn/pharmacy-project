from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where contact_number is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, contact_number, password=None, **extra_fields):
        """
        Create and save a User with the given contact_number and password.
        """
        if not contact_number:
            raise ValueError('The Contact Number must be set')
        user = self.model(contact_number=contact_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, contact_number, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given contact_number and password.
        """
        # Ensure the Admin role exists and assign it
        admin_role, _ = Role.objects.get_or_create(name='Admin')
        extra_fields.setdefault('role', admin_role)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(contact_number, password, **extra_fields)


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    # By setting these to None, we remove the inherited first_name and last_name fields.
    # This makes `full_name` the single source of truth for the user's name.
    first_name = None
    last_name = None
    email = None
    username = None

    contact_number = models.CharField(max_length=20, unique=True, help_text="The contact number used for login.")
    full_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'contact_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically set staff and superuser status
        based on the assigned role.
        """
        if self.role and self.role.name == 'Admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.contact_number

class Location(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # e.g., استان, شهرستان, شهر, منطقه
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.name} ({self.type})"

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Drug(models.Model):
    generic_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100, blank=True, null=True)
    irc = models.CharField(max_length=20, unique=True)
    dosage = models.CharField(max_length=50)
    form = models.CharField(max_length=50)  # e.g., Tablet, Syrup, Injection
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    requires_prescription = models.BooleanField(default=True)
    image = models.ImageField(upload_to='drugs/', blank=True, null=True)

    def __str__(self):
        return f"{self.generic_name} ({self.brand_name or ''})"

class Pharmacy(models.Model):
    name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=50, unique=True)
    owner_full_name = models.CharField(max_length=100)
    owner_phone_number = models.CharField(max_length=20)
    pharmacist_full_name = models.CharField(max_length=100)
    pharmacist_phone_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    is_24_hours = models.BooleanField(default=False)
    address = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='pharmacies/', blank=True, null=True)

    def __str__(self):
        return self.name

class PharmacyInventory(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name_plural = "Pharmacy Inventories"

    def __str__(self):
        return f"{self.drug.generic_name} at {self.pharmacy.name}"

class InventorySearchLog(models.Model):
    """Logs search queries made to the pharmacy inventory endpoint."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    query_params = models.TextField(help_text="The search query parameters as a JSON string.")
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_identifier = self.user.contact_number if self.user else 'Anonymous'
        return f"Search by {user_identifier} at {self.timestamp}"

class RequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    request_payload = models.TextField(blank=True, null=True)
    response_status = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.response_status}"
