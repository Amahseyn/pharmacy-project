from .models import RequestLog
import json
import copy

class RequestLogMiddleware:
    """
    Middleware to log API requests to the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Make a copy of the request body before it's consumed by the view.
        # This is safe because request.body is a bytestring that is cached
        # on its first read. We access it here to ensure it's cached.
        request_body_copy = copy.copy(request.body)

        # Paths to exclude from logging
        exclude_paths = ['/api/swagger/', '/api/redoc/']

        # Process the request and get the response before logging
        response = self.get_response(request) # The view consumes the original request body here.

        # We only want to log API requests, not admin or documentation pages.
        # Also, avoid logging OPTIONS pre-flight requests which are common with CORS.
        if request.path.startswith('/api/') and request.path not in exclude_paths and request.method != 'OPTIONS':
            user = request.user if request.user.is_authenticated else None

            # Get the client's real IP address, handling proxies
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Safely capture the request body (for POST/PUT) or query params (for GET)
            request_payload = "" # Default to empty string
            if request.method == 'GET' and request.GET:
                # For GET requests, log the query parameters
                request_payload = json.dumps(request.GET)
            elif request_body_copy:
                try:
                    if 'application/json' in request.content_type:
                        payload = json.loads(request_body_copy)
                        # Censor sensitive fields like 'password' before logging
                        if 'password' in payload:
                            payload['password'] = '********'
                        request_payload = json.dumps(payload)
                    else:
                        # Avoid logging large file uploads, etc.
                        request_payload = f"Non-JSON body (Content-Type: {request.content_type})"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request_payload = "Could not decode request body."

            # Create the log entry in the database
            RequestLog.objects.create(
                user=user,
                endpoint=request.path,
                method=request.method,
                request_payload=request_payload,
                response_status=response.status_code,
                ip_address=ip_address,
            )

        return response