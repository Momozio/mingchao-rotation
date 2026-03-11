"""
Django middleware to add COOP and COEP headers for SharedArrayBuffer support.
This is required for FFmpeg.wasm to work properly.

Add this middleware to your MIDDLEWARE setting in settings.py:
    MIDDLEWARE = [
        # ... other middleware
        'middleware.shared_array_buffer_middleware.SharedArrayBufferMiddleware',
    ]
"""


class SharedArrayBufferMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add headers for SharedArrayBuffer support (required for FFmpeg.wasm)
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"

        return response
