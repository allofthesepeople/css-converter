# -*- coding: utf-8 -*-

# Stdlib
import json
import importlib

# Third party
from flask import Flask
from flask import g
from flask import request
from flask import Response

# Local
from processors.exceptions import ValidationError

app = Flask(__name__)


@app.before_request
def header_check():
    """
    Compltes basic processing on the request before being sent to the main
    function for handling.
    """
    if request.content_type != 'text/csv':
        return respond_with(
            {'Error': 'Only accepts `Content-Type: text/csv only`'},
            415)

    g.input_data = request.get_data().decode('utf-8')

    if len(g.input_data) < 0:
        return respond_with({'Error': 'No CSV data found'}, 400)


@app.route("/<processor>", methods=['POST'])
def convert(processor):
    """
    The primary http route.

    Attempts to import the correct processor & process the body.
    """
    # Attempt to get the correct processor
    try:
        import_path = "processors.{}_processor".format(processor)
        package = importlib.import_module(import_path)
        processor = getattr(package, "{}Processor".format(processor.title()))
    except (ImportError, AttributeError):
        return respond_with({'Error': 'No Processor found'}, 404)

    # Try to process the request body
    try:
        processed = processor(g.input_data)
    except ValidationError:
        msg = '{}'.format(', '.join(g.get('errors')))
        return respond_with({'Validation Error(s)': msg}, 400)

    return respond_with(processed.rows, 200)


def respond_with(data, status):
    """
    Attempts to return the data in the format requested.

    NOTE: Curently only works with JSON.
    """
    # If Accept Header is not provided or if it’s application/json
    if (request.headers.get('accept') == 'application/json' or
            request.headers.get('accept') == '*/*' or
            request.headers.get('accept') is None):
        return Response(json.dumps(data),
                        status=status,
                        mimetype='application/json')

    # Additional return formats can be added here
    return ('Only accepts `Accept: application/json only`', 406)


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
