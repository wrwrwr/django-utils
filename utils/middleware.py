import re


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
            response.content = str(tidy.parseString(content, **options))
        return response
