class NoCacheAuthenticatedPagesMiddleware:
    AUTH_PATHS = {
        '/login/',
        '/logout/',
        '/register/',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated or request.path in self.AUTH_PATHS:
            response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response