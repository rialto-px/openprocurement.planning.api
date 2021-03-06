# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.auth import DEFAULT_OPERATOR
from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.migration import migrate_data, get_db_schema_version, set_db_schema_version, SCHEMA_VERSION
from openprocurement.planning.api.tests.base import test_plan_data, BaseWebTest


class MigrateTest(BaseWebTest):

    def test_migrate(self):
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)
        migrate_data(self.app.app.registry)
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)

    def test_migrate_from0to1(self):
        set_db_schema_version(self.db, 0)
        u = Plan(test_plan_data)
        u.planID = "UA-X"
        u.store(self.db)
        data = self.db.get(u.id)
        data["documents"] = [
            {
                "id": "ebcb5dd7f7384b0fbfbed2dc4252fa6e",
                "title": "name.txt",
                "documentOf": "tender",
                "url": "/tenders/{}/documents/ebcb5dd7f7384b0fbfbed2dc4252fa6e?download=10367238a2964ee18513f209d9b6d1d3".format(u.id),
                "datePublished": "2016-06-01T00:00:00+03:00",
                "dateModified": "2016-06-01T00:00:00+03:00",
                "format": "text/plain",
            }
        ]
        _id, _rev = self.db.save(data)
        self.app.app.registry.docservice_url = 'http://localhost'
        migrate_data(self.app.app.registry, 1)
        migrated_item = self.db.get(u.id)
        self.assertIn('http://localhost/get/10367238a2964ee18513f209d9b6d1d3?', migrated_item['documents'][0]['url'])
        self.assertIn('Prefix={}%2Febcb5dd7f7384b0fbfbed2dc4252fa6e'.format(u.id), migrated_item['documents'][0]['url'])
        self.assertIn('KeyID=', migrated_item['documents'][0]['url'])
        self.assertIn('Signature=', migrated_item['documents'][0]['url'])

    def test_migrate_from1to2(self):
        set_db_schema_version(self.db, 1)
        data = {'doc_type': 'Plan'}
        _id, _rev = self.db.save(data)
        migrate_data(self.app.app.registry, 2)
        migrated_item = self.db.get(_id)
        self.assertIn('operator', migrated_item)
        self.assertEqual(migrated_item['operator'], DEFAULT_OPERATOR)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
