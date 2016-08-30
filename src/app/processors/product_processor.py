# -*- coding: utf-8 -*-

# local
from .base_processor import BaseProcessor
from .exceptions import ValidationError


class ProductProcessor(BaseProcessor):
    header_adj = [('item_id', 'id')]
    nested_fields = [('modifier', 'modifiers')]
    required_fields = ['price_type']

    def fld__price_type(self, val):
        """
        Validate the `price_type` property
        """
        if val.strip() not in ('system', 'open'):
            raise ValidationError("`price_type` must be 'system' or 'open'")

    def fld__price(self, val):
        """
        Example modification to the `price` property
        """
        return val

    def fld__modifiers__name(self, val):
        """
        Example modification to the nested `name` property
        """
        return val
