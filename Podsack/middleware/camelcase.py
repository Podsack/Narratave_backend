import re
import json
import time


class CamelCaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        # Convert request data from camelCase to snake_case
        self.convert_request_data(request)
        print(f"request time taken {time.time() - start} ms")

        response = self.get_response(request)

        # Convert response JSON keys from snake_case to camelCase
        if response.get('Content-Type', '').startswith('application/json'):
            start = time.time()
            self.convert_response_data(response)
            print(f"response time taken {time.time() - start} ms")

        return response

    def convert_request_data(self, request):
        if request.content_type == 'application/json':
            request_data = json.loads(request.body)

            # Convert request JSON keys from camelCase to snake_case
            converted_data = self.convert_keys(request_data, camel_to_snake=True)

            # Update the request body with the converted data
            request._body = json.dumps(converted_data).encode('UTF-8')

    def convert_response_data(self, response):
        content = response.content.decode('utf-8')
        content_type = response.headers['Content-Type']

        if content_type.startswith('application/json'):
            response_data = json.loads(content)

            # Convert response JSON keys from snake_case to camelCase
            converted_data = self.convert_keys(response_data, camel_to_snake=False)

            # Update the response content with the converted data
            response.content = json.dumps(converted_data)

    def convert_keys(self, data, camel_to_snake):
        if isinstance(data, dict):
            converted = {}
            for key, value in data.items():
                converted_key = self.convert_key_case(key, camel_to_snake)
                converted_value = self.convert_keys(value, camel_to_snake)
                converted[converted_key] = converted_value
            return converted
        elif isinstance(data, list):
            return [self.convert_keys(item, camel_to_snake) for item in data]
        else:
            return data

    @staticmethod
    def convert_key_case(key, camel_to_snake):
        if camel_to_snake:
            # Convert camelCase to snake_case
            return re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        else:
            # Convert snake_case to camelCase
            parts = iter(key.split('_'))
            return next(parts) + ''.join(word.title() for word in parts)
