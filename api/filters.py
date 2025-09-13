import django_filters
from .models import (
    Location, Manufacturer, Drug, Pharmacy, PharmacyInventory, User, InventorySearchLog)


class LocationFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Location Name",
		help_text="Filter by location name (e.g., 'Tehran'). Case-insensitive, partial match."
	)
	type = django_filters.CharFilter(
		lookup_expr='exact',
		label="Location Type",
		help_text="Filter by location type (e.g., 'استان', 'شهر'). Exact match."
	)
	parent = django_filters.NumberFilter(
		lookup_expr='exact',
		label="Parent Location ID",
		help_text="Filter by the ID of the parent location."
	)
	parent_name = django_filters.CharFilter(
		field_name='parent__name',
		lookup_expr='icontains',
		label="Parent Location Name",
		help_text="Filter by the name of the parent location. Case-insensitive, partial match."
	)

	class Meta:
		model = Location
		# When filters are defined explicitly above, 'fields' is not needed.
		fields = []


class ManufacturerFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Manufacturer Name",
		help_text="Filter by manufacturer name. Case-insensitive, partial match."
	)
	country = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Country",
		help_text="Filter by country of origin. Case-insensitive, partial match."
	)

	class Meta:
		model = Manufacturer
		fields = []

class DrugFilter(django_filters.FilterSet):
	generic_name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Generic Name",
		help_text="Filter by drug's generic name. Case-insensitive, partial match."
	)
	brand_name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Brand Name",
		help_text="Filter by drug's brand name. Case-insensitive, partial match."
	)
	manufacturer = django_filters.NumberFilter(
		lookup_expr='exact',
		label="Manufacturer ID",
		help_text="Filter by the ID of the manufacturer."
	)
	manufacturer_name = django_filters.CharFilter(
		field_name='manufacturer__name',
		lookup_expr='icontains',
		label="Manufacturer Name",
		help_text="Filter by manufacturer name. Case-insensitive, partial match."
	)
	form = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Drug Form",
		help_text="Filter by drug form (e.g., 'Tablet', 'Syrup'). Case-insensitive, partial match."
	)
	irc = django_filters.CharFilter(
		lookup_expr='exact',
		label="IRC Code",
		help_text="Filter by the exact drug registration code (IRC)."
	)
	requires_prescription = django_filters.BooleanFilter(
		label="Requires Prescription",
		help_text="Filter for drugs that require a prescription (true/false)."
	)

	class Meta:
		model = Drug
		fields = []


class PharmacyFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Pharmacy Name",
		help_text="Filter by pharmacy name. Case-insensitive, partial match."
	)
	location = django_filters.NumberFilter(
		lookup_expr='exact',
		label="Location ID",
		help_text="Filter by the ID of the pharmacy's location."
	)
	location_name = django_filters.CharFilter(
		field_name='location__name',
		lookup_expr='icontains',
		label="Location Name",
		help_text="Filter by the pharmacy's location name. Case-insensitive, partial match."
	)
	is_24_hours = django_filters.BooleanFilter(
		label="Is 24 Hours",
		help_text="Filter for pharmacies that are open 24 hours (true/false)."
	)
	license_number = django_filters.CharFilter(
		lookup_expr='exact',
		label="License Number",
		help_text="Filter by the exact pharmacy license number."
	)
	owner_full_name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Owner Name",
		help_text="Filter by pharmacy owner's name. Case-insensitive, partial match."
	)
	pharmacist_full_name = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Pharmacist Name",
		help_text="Filter by pharmacist's name. Case-insensitive, partial match."
	)

	class Meta:
		model = Pharmacy
		fields = []


class PharmacyInventoryFilter(django_filters.FilterSet):
	drug = django_filters.NumberFilter(
		lookup_expr='exact',
		label="Drug ID",
		help_text="Filter by the ID of the drug."
	)
	drug_name = django_filters.CharFilter(
		field_name='drug__generic_name',
		lookup_expr='icontains',
		label="Drug Generic Name",
		help_text="Filter by the drug's generic name. Case-insensitive, partial match."
	)
	drug_brand_name = django_filters.CharFilter(
		field_name='drug__brand_name',
		lookup_expr='icontains',
		label="Drug Brand Name",
		help_text="Filter by the drug's brand name. Case-insensitive, partial match."
	)
	drug_form = django_filters.CharFilter(
		field_name='drug__form',
		lookup_expr='icontains',
		label="Drug Form",
		help_text="Filter by drug form (e.g., 'Tablet'). Case-insensitive, partial match."
	)
	drug_irc = django_filters.CharFilter(
		field_name='drug__irc',
		lookup_expr='exact',
		label="Drug IRC Code",
		help_text="Filter by the exact drug registration code (IRC)."
	)
	manufacturer_name = django_filters.CharFilter(
		field_name='drug__manufacturer__name',
		lookup_expr='icontains',
		label="Manufacturer Name",
		help_text="Filter by the drug's manufacturer name. Case-insensitive, partial match."
	)
	pharmacy = django_filters.NumberFilter(
		lookup_expr='exact',
		label="Pharmacy ID",
		help_text="Filter by the ID of the pharmacy."
	)
	pharmacy_name = django_filters.CharFilter(
		field_name='pharmacy__name',
		lookup_expr='icontains',
		label="Pharmacy Name",
		help_text="Filter by the pharmacy's name. Case-insensitive, partial match."
	)
	pharmacy_is_24_hours = django_filters.BooleanFilter(
		field_name='pharmacy__is_24_hours',
		label="Is 24 Hours",
		help_text="Filter for pharmacies that are open 24 hours (true/false)."
	)
	location_district = django_filters.CharFilter(
		field_name='pharmacy__location__name',
		lookup_expr='icontains',
		label="District Name",
		help_text="Filter by district name (e.g., 'منطقه ۱'). Assumes a 4-level hierarchy."
	)
	location_city = django_filters.CharFilter(
		field_name='pharmacy__location__parent__name',
		lookup_expr='icontains',
		label="City Name",
		help_text="Filter by city name (e.g., 'تهران')."
	)
	location_county = django_filters.CharFilter(
		field_name='pharmacy__location__parent__parent__name',
		lookup_expr='icontains',
		label="County Name",
		help_text="Filter by county name (e.g., 'کرج')."
	)
	location_province = django_filters.CharFilter(
		field_name='pharmacy__location__parent__parent__parent__name',
		lookup_expr='icontains',
		label="Province Name",
		help_text="Filter by province name (e.g., 'البرز')."
	)
	batch_number = django_filters.CharFilter(
		lookup_expr='icontains',
		label="Batch Number",
		help_text="Filter by batch number. Case-insensitive, partial match."
	)
	has_stock = django_filters.BooleanFilter(field_name='quantity', lookup_expr='gt', initial=True, help_text="Filter for items with quantity greater than 0.")
	expire_date = django_filters.DateFromToRangeFilter(
		label="Expiration Date Range",
		help_text="Filter by expiration date range. Use 'expire_date_after' and 'expire_date_before'."
	)
	price = django_filters.RangeFilter(
		label="Price Range",
		help_text="Filter by price range. Use 'price_min' and 'price_max'."
	)


	class Meta:
		model = PharmacyInventory
		fields = []


class UserFilter(django_filters.FilterSet):
	# برای فیلد role که از نوع SlugRelatedField است، باید نوع فیلتر را مشخص کنیم
	role = django_filters.CharFilter(field_name='role__name', lookup_expr='exact', label="Role Name", help_text="Filter users by role name (e.g., 'Admin', 'User').")

	class Meta:
		model = User
		fields = []


class InventorySearchLogFilter(django_filters.FilterSet):
	"""FilterSet for the InventorySearchLog model."""
	user = django_filters.NumberFilter(field_name='user__id', label="User ID")
	contact_number = django_filters.CharFilter(field_name='user__contact_number', lookup_expr='icontains', label="User Contact Number")
	ip_address = django_filters.CharFilter(lookup_expr='exact', label="IP Address")
	timestamp_after = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='gte')
	timestamp_before = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='lte')
	query_params = django_filters.CharFilter(lookup_expr='icontains', label="Query Parameters")

	class Meta:
		model = InventorySearchLog
		fields = ['user', 'ip_address', 'query_params']