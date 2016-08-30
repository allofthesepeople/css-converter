# -*- coding: utf-8 -*-

# Stdlib
import json
import unittest

# local
import app


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_correct_content_type(self):
        body = "foo,price_type\nbar,system"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/json'},
                            data=body)
        data = json.loads(req.get_data().decode("utf-8"))
        assert '200' in req.status
        assert data[0].get('foo') == 'bar'
        assert data[0].get('modifiers') == []

    def test_incorrect_content_type(self):
        req = self.app.post('/product', content_type='application/json')
        assert '415' in req.status

    def test_unkown_accept_header(self):
        body = "foo,price_type\nbar,system"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/xml'},
                            data=body)
        assert '406' in req.status

    def test_header_converstion(self):
        body = "item id,price_type\n1000,open"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/json'},
                            data=body)
        data = json.loads(req.get_data().decode("utf-8"))
        assert '200' in req.status
        assert 'id' in data[0].keys()
        assert 'item id' not in data[0].keys()
        assert 'item_id' not in data[0].keys()

    def test_nested_content(self):
        body = "modifier_1_name,price_type\nfoo,open"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/json'},
                            data=body)
        data = json.loads(req.get_data().decode("utf-8"))
        assert '200' in req.status
        assert 'name' in data[0].get('modifiers')[0].keys()
        assert 'foo' == data[0].get('modifiers')[0].get('name')

    def test_required_field_raises_error(self):
        body = "foo\nbar"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/json'},
                            data=body)
        assert '400' in req.status

    def test_validation_field_raises_error(self):
        body = "price_type\nfoo"
        req = self.app.post('/product',
                            content_type='text/csv',
                            headers={'accept': 'application/json'},
                            data=body)
        assert '400' in req.status

if __name__ == '__main__':
    unittest.main()
