# -*- encoding: utf-8 -*-
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import testtools

from ironicclient.tests import utils
import ironicclient.v1.node

NODE = {'id': 123,
        'uuid': '66666666-7777-8888-9999-000000000000',
        'chassis_id': 42,
        'driver': 'fake',
        'driver_info': {'user': 'foo', 'password': 'bar'},
        'properties': {'num_cpu': 4},
        'extra': {}}

PORT = {'id': 456,
        'uuid': '11111111-2222-3333-4444-555555555555',
        'node_id': 123,
        'address': 'AA:AA:AA:AA:AA:AA',
        'extra': {}}

POWER_STATE = {'current': 'power off',
               'target': 'power on'}

CREATE_NODE = copy.deepcopy(NODE)
del CREATE_NODE['id']
del CREATE_NODE['uuid']

UPDATED_NODE = copy.deepcopy(NODE)
NEW_DRIVER = 'new-driver'
UPDATED_NODE['driver'] = NEW_DRIVER

fixtures = {
    '/v1/nodes':
    {
        'GET': (
            {},
            {"nodes": [NODE]},
        ),
        'POST': (
            {},
            CREATE_NODE,
        ),
    },
    '/v1/nodes/%s' % NODE['uuid']:
    {
        'GET': (
            {},
            NODE,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_NODE,
        ),
    },
    '/v1/nodes/%s/ports' % NODE['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/state/power' % NODE['uuid']:
    {
        'PUT': (
            {},
            POWER_STATE,
        ),
    },
}


class NodeManagerTest(testtools.TestCase):

    def setUp(self):
        super(NodeManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ironicclient.v1.node.NodeManager(self.api)

    def test_node_list(self):
        node = self.mgr.list()
        expect = [
            ('GET', '/v1/nodes', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(node), 1)

    def test_node_show(self):
        node = self.mgr.get(NODE['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s' % NODE['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(node.uuid, NODE['uuid'])

    def test_create(self):
        node = self.mgr.create(**CREATE_NODE)
        expect = [
            ('POST', '/v1/nodes', {}, CREATE_NODE),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(node)

    def test_delete(self):
        node = self.mgr.delete(node_id=NODE['uuid'])
        expect = [
            ('DELETE', '/v1/nodes/%s' % NODE['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(node is None)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DRIVER,
                 'path': '/driver'}
        node = self.mgr.update(node_id=NODE['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE['uuid'], {}, patch),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(node.driver, NEW_DRIVER)

    def test_node_port_list(self):
        ports = self.mgr.list_ports(NODE['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/ports' % NODE['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0].uuid, PORT['uuid'])
        self.assertEqual(ports[0].address, PORT['address'])

    def test_node_set_power_state(self):
        power_state = self.mgr.set_power_state(NODE['uuid'], "on")
        body = {'target': 'power on'}
        expect = [
            ('PUT', '/v1/nodes/%s/state/power' % NODE['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power on', power_state.target)
