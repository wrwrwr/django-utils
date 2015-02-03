import re

from django.conf import settings


STARTING_BLANK_LINES = re.compile(r'^\n+')
TRAILING_BLANK_LINES = re.compile(r'\n+$')

WHITESPACE_LINES = re.compile(r'^[^\S\n]+\n', re.MULTILINE)

TIDY_OPTIONS = {'indent': 'auto', 'wrap': 0}


class NoStartingTrailingBlankLinesMiddleware:
    """
    Removes blank lines at the begginging and at the end of output
    (whole response).
    """
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = STARTING_BLANK_LINES.sub('', response.content)
            response.content = TRAILING_BLANK_LINES.sub('', response.content)
        return response


class NoWhitespaceLinesMiddleware:
    """
    Removes all whitespace only (but non-empty) lines in output.
    """
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = WHITESPACE_LINES.sub('', response.content)
        return response


class TidyMiddleware:
    """
    Runs output through Tidy.
    """
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            import tidy
            response.content = str(tidy.parseString(response.content))
        return response


class CSPMiddleware:
    """
    Adds different content security headers to every response.

    X-Frame-Options:
        https://developer.mozilla.org/en/The_X-FRAME-OPTIONS_response_header
    X-Content-Security-Policy:
        https://wiki.mozilla.org/Security/CSP/Specification
    X-WebKit-CSP:
        http://blog.chromium.org/2011/06/new-chromium-security-features-june.html
    Content-Security-Policy:
        http://www.w3.org/TR/CSP/

    On default all headers are set to only allow content from the same domain,
    you may control each header by defining: ``X_FRAME_OPTIONS``,
    ``X_CONTENT_SECURITY_POLICY`` or ``CONTENT_SECURITY_POLICY`` in your
    settings. Set it to None to avoid adding a header completely.

    TODO:
    -- Update to match changes in the standard (particularly
       X-Content-Security-Policy and X-WebKit-CSP should be removed).
    -- Maybe just let user define one constant (CONTENT_SECURITY_POLICY),
       send the same headers for WebKit and Gecko and deduce X-Frame-Options
       from it?
    -- Good collection of other options: http://drupal.org/project/seckit.
    -- Exempt decorator.
    """
    def process_response(self, request, response):

        # Don't set it if there is an exempt.
        if getattr(response, 'csp_exempt', False):
            return response

        # X-Frame-Options defaults to "SAMEORIGIN" (explicitely setting
        # to None disables).
        x_frame_options = getattr(
            settings, 'X_FRAME_OPTIONS', 'SAMEORIGIN').upper()
        if x_frame_options is not None and 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = x_frame_options

        # TODO: Should X-Content-Security-Policy now default to
        #       "allow: 'self'" or "default-src \'self\'"?
        x_content_security_policy = getattr(
            settings, 'X_CONTENT_SECURITY_POLICY', 'default-src \'self\'')
        if (x_content_security_policy is not None and
                'X-Content-Security-Policy' not in response):
            response['X-Content-Security-Policy'] = x_content_security_policy

        # X-WebKit-CSP is a temporary name for Content-Security-Policy
        # in WebKit browsers.
        x_webkit_csp = getattr(
            settings, 'X_WEBKIT_CSP', 'default-src \'self\'')
        if x_webkit_csp is not None and 'X-WebKit-CSP' not in response:
            response['X-WebKit-CSP'] = x_webkit_csp

        # Content-Security-Policy defaults to "default-src 'self'".
        content_security_policy = getattr(
            settings, 'CONTENT_SECURITY_POLICY', 'default-src \'self\'')
        if (content_security_policy is not None and
                'Content-Security-Policy' not in response):
            response['Content-Security-Policy'] = content_security_policy

        return response
