from rest_framework.permissions import BasePermission

class IsAdminOrSuperUser(BasePermission):
	"""
	Allows access only to superusers or users with the 'Admin' role.
	"""
	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role and request.user.role.name == 'Admin')