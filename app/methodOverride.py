from urllib.parse import parse_qs
from io import BytesIO
from werkzeug.formparser import parse_form_data 

class MethodOverrideMiddleware:
    allowed_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0

            request_body = environ['wsgi.input'].read(request_body_size)
            environ['wsgi.input'] = BytesIO(request_body)

            content_type = environ.get('CONTENT_TYPE', '')
            
            if 'multipart/form-data' in content_type:
                _, form, _ = parse_form_data(environ)
                if '_method' in form:
                    method = form['_method'].upper()
                    if method in self.allowed_methods:
                        environ['REQUEST_METHOD'] = method
            else:
                try:
                    form_data = parse_qs(request_body.decode('utf-8'))
                    method = form_data.get('_method', [''])[0].upper()
                    if method in self.allowed_methods:
                        environ['REQUEST_METHOD'] = method
                except UnicodeDecodeError:
                    pass

            environ['wsgi.input'].seek(0)

        return self.app(environ, start_response)