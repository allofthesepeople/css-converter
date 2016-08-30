# -*- coding: utf-8 -*-

# Stdlib
import csv
from collections import OrderedDict
from io import StringIO

# Local
from .exceptions import ValidationError


class BaseProcessor(object):
    """
    Base processor to be extended by the individual processors
    """

    # A list of tuples for header name replacement
    header_adj = []

    # nested_headers should be a list of tuples overridden by the individual
    # processors. 1st item is the requested field name suffix, and the
    # (optional) second parameter is the field name in the returned format.
    nested_fields = []

    # Any required fields
    required_fields = []

    def __init__(self, input_data):
        """
        Processes the raw data and converts to a list of dictionaries.
        """
        buf = self.process_headers(StringIO(input_data))
        reader = csv.DictReader(buf)
        self.rows = [self.process_row(row) for row in reader]

    def __call__(self):
        """
        Make the class callable

        The whole process is only converting csv => list of dictionaries, so we
        only need the one function. It’s been split into various methods for
        inheritance and legibility.
        """
        return self.rows

    def process_headers(self, buf):
        """
        Header normalisation and replacement

        Normalisaton consists of trimmed, lowercase & replace ' ' => '_'
        """
        lines = buf.readlines()
        headers = []

        # Process each header, this could probably be writtena better as a list
        # comprehension but it may not be as readable

        for idx, header in enumerate(lines[0].lower().split(',')):
            header = header.strip().replace(' ', '_')

            if not self.header_adj or len(self.header_adj) == 0:
                headers.append(header)
                continue

            # Do any adjustments
            included = False
            for (old, new) in self.header_adj:
                if header == old:
                    headers.append(new)
                    included = True
                    continue

            if included is False:
                headers.append(header)

        # Convert back to a line in the string
        headers = ','.join(headers)
        lines[0] = headers + "\n"

        # Save the new headers list back as a buffer
        data = '\n'.join(lines)
        return StringIO(data)

    def process_row(self, row):
        """
        Processes each row and fields within

        Primarily handles nesting and applying of any modifiers present on the
        child class.
        """
        # First add in the nested props
        processed_row = {out_name: {} for (_, out_name) in self.nested_fields}

        for key, val in row.items():
            for (in_name, out_name) in self.nested_fields:
                if key.startswith(in_name):
                    # Get position & nested dict key getting the head & tail
                    # Requires python 3 `*` operator
                    idx, *nested_name = key.lstrip(in_name)[1:].split('_')

                    # Convert any possible names as lists back to a string
                    nested_name = '_'.join(nested_name)

                    for adj in self.header_adj:
                        if adj[0] == '{}.{}'.format(out_name, nested_name):
                            nested_name = adj[1]

                    # Gets the name of a modifying method
                    fld_method_key = '{}__{}'.format(out_name, nested_name)

                    # Get the value using the modifying method (if exists)
                    adj_val = self.assign_fld_val(fld_method_key, val)

                    try:
                        processed_row[out_name][idx][nested_name] = adj_val
                    except KeyError:
                        processed_row[out_name][idx] = OrderedDict()
                        processed_row[out_name][idx][nested_name] = adj_val
                else:
                    processed_row[key] = self.assign_fld_val(key, val)

        for required_fld in self.required_fields:
            if required_fld not in processed_row.keys():
                raise ValidationError(
                    '`{}` is a required field'.format(required_fld))

        # Now need to convert the OrderedDict to a list
        for (_, out_name) in self.nested_fields:
            processed_row[out_name] = list(processed_row[out_name].values())

        return processed_row

    def assign_fld_val(self, key, val):
        """
        Allows per-field functions to apply validation/changes

        Follows the convention of `fld__<key_name>`, nested fields follow the
        convention of `fld__<parent_key_name>__<child_key_name>`.
        """
        try:
            fld_method = getattr(self, 'fld__'+key)
            return fld_method(val)
        except AttributeError:
            return val
