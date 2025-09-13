from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to allow disabling pagination with `page=0`
    and to set a default page size and a client-overridable limit.
    """
    page_size = 5  # Default number of items to return per page.
    page_size_query_param = 'limit'  # Client can override page size with this parameter.
    max_page_size = 100  # Maximum limit a client can request.

    def paginate_queryset(self, queryset, request, view=None):
        """
        Overrides the default behavior to handle the case where page=0
        is requested, which should disable pagination and return all results.
        """
        page_number = request.query_params.get(self.page_query_param)

        # If 'page=0' is present in the query params, disable pagination.
        if page_number and page_number.isdigit() and int(page_number) == 0:
            return None  # Returning None tells DRF to not paginate.

        return super().paginate_queryset(queryset, request, view)