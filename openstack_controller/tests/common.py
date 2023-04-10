# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import datetime
import json
import os
from urllib.parse import urlparse

from datadog_checks.dev.fs import get_here
from datadog_checks.dev.http import MockResponse

CHECK_NAME = 'openstack'

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
TEST_OPENSTACK_CONFIG_PATH = os.path.join(FIXTURES_DIR, 'openstack_config.yaml')
TEST_OPENSTACK_NO_AUTH_CONFIG_PATH = os.path.join(FIXTURES_DIR, 'openstack_bad_config.yaml')

USE_OPENSTACK_SANDBOX = os.environ.get('USE_OPENSTACK_SANDBOX')

ALL_IDS = ['server-1', 'server-2', 'other-1', 'other-2']
EXCLUDED_NETWORK_IDS = ['server-1', 'other-.*']
EXCLUDED_SERVER_IDS = ['server-2', 'other-.*']
FILTERED_NETWORK_ID = 'server-2'
FILTERED_SERVER_ID = 'server-1'
FILTERED_BY_PROJ_SERVER_ID = ['server-1', 'server-2']

CONFIG = {
    'keystone_server_url': 'http://127.0.0.1:8080/identity',
    'username': 'admin',
    'password': 'password',
}

CONFIG_NOVA_MICROVERSION_LATEST = {
    'keystone_server_url': 'http://127.0.0.1:8080/identity',
    'username': 'admin',
    'password': 'password',
    'nova_microversion': 'latest',
}

KEYSTONE_INSTANCE = {
    'name': 'test_name',
    'keystone_server_url': 'http://10.0.2.15:5000',
    'user': {'name': 'test_name', 'password': 'test_pass', 'domain': {'id': 'test_id'}},
    'ssl_verify': False,
    'exclude_network_ids': EXCLUDED_NETWORK_IDS,
}

MOCK_CONFIG = {'init_config': {}, 'instances': [KEYSTONE_INSTANCE]}

EXAMPLE_AUTH_RESPONSE = {
    u'token': {
        u'methods': [u'password'],
        u'roles': [
            {u'id': u'f20c215f5a4d47b7a6e510bc65485ced', u'name': u'datadog_monitoring'},
            {u'id': u'9fe2ff9ee4384b1894a90878d3e92bab', u'name': u'_member_'},
        ],
        u'expires_at': u'2015-11-02T15: 57: 43.911674Z',
        u'project': {
            u'domain': {u'id': u'default', u'name': u'Default'},
            u'id': u'0850707581fe4d738221a72db0182876',
            u'name': u'admin',
        },
        u'catalog': [
            {
                u'endpoints': [
                    {
                        u'url': u'http://10.0.2.15:8774/v2.1/0850707581fe4d738221a72db0182876',
                        u'interface': u'internal',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'354e35ed19774e398f80dc2a90d07f4b',
                    },
                    {
                        u'url': u'http://10.0.2.15:8774/v2.1/0850707581fe4d738221a72db0182876',
                        u'interface': u'public',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'36e8e2bf24384105b9d56a65b0900172',
                    },
                    {
                        u'url': u'http://10.0.2.15:8774/v2.1/0850707581fe4d738221a72db0182876',
                        u'interface': u'admin',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'de93edcbf7f9446286687ec68423c36f',
                    },
                ],
                u'type': u'compute',
                u'id': u'2023bd4f451849ba8abeaaf283cdde4f',
                u'name': u'nova',
            },
            {
                u'endpoints': [
                    {
                        u'url': u'http://10.0.3.111:8776/v1/***************************4bfc1',
                        u'interface': u'public',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'***************************2452f',
                    },
                    {
                        u'url': u'http://10.0.2.15:8776/v1/***************************4bfc1',
                        u'interface': u'admin',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'***************************8239f',
                    },
                    {
                        u'url': u'http://10.0.2.15:8776/v1/***************************4bfc1',
                        u'interface': u'internal',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'***************************7caa1',
                    },
                ],
                u'type': u'volume',
                u'id': u'***************************e7e16',
                u'name': u'cinder',
            },
            {
                u'endpoints': [
                    {
                        u'url': u'http://10.0.2.15:9292',
                        u'interface': u'internal',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'7c1e318d8f7f42029fcb591598df2ef5',
                    },
                    {
                        u'url': u'http://10.0.2.15:9292',
                        u'interface': u'public',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'afcc88b1572f48a38bb393305dc2b584',
                    },
                    {
                        u'url': u'http://10.0.2.15:9292',
                        u'interface': u'admin',
                        u'region': u'RegionOne',
                        u'region_id': u'RegionOne',
                        u'id': u'd9730dbdc07844d785913219da64a197',
                    },
                ],
                u'type': u'network',
                u'id': u'21ad241f26194bccb7d2e49ee033d5a2',
                u'name': u'neutron',
            },
        ],
        u'extras': {},
        u'user': {
            u'domain': {u'id': u'default', u'name': u'Default'},
            u'id': u'5f10e63fbd6b411186e561dc62a9a675',
            u'name': u'datadog',
        },
        u'audit_ids': [u'OMQQg9g3QmmxRHwKrfWxyQ'],
        u'issued_at': u'2015-11-02T14: 57: 43.911697Z',
    }
}

EXAMPLE_PROJECTS_RESPONSE = {
    "projects": [
        {
            "domain_id": "1789d1",
            "enabled": True,
            "id": "263fd9",
            "links": {"self": "https://example.com/identity/v3/projects/263fd9"},
            "name": "Test Group",
        }
    ],
    "links": {"self": "https://example.com/identity/v3/auth/projects", "previous": None, "next": None},
}

# .. server/network
SERVERS_CACHE_MOCK = {
    'servers': {
        "server-1": {"id": "server-1", "name": "server-name-1", "status": "ACTIVE", "project_name": "testproj"},
        "server-2": {"id": "server-2", "name": "server-name-2", "status": "ACTIVE", "project_name": "testproj"},
        "other-1": {"id": "other-1", "name": "server-name-other-1", "status": "ACTIVE", "project_name": "blacklist_1"},
        "other-2": {"id": "other-2", "name": "server-name-other-2", "status": "ACTIVE", "project_name": "blacklist_2"},
    },
    'change_since': datetime.datetime.utcnow().isoformat(),
}

EMPTY_NOVA_SERVERS = []

# One example from MOCK_NOVA_SERVERS to emulate pagination
MOCK_NOVA_SERVERS_PAGINATED = [
    {
        "OS-DCF:diskConfig": "AUTO",
        "OS-EXT-AZ:availability_zone": "nova",
        "OS-EXT-SRV-ATTR:host": "compute",
        "OS-EXT-SRV-ATTR:hostname": "server-1",
        "OS-EXT-SRV-ATTR:hypervisor_hostname": "fake-mini",
        "OS-EXT-SRV-ATTR:instance_name": "instance-00000001",
        "OS-EXT-SRV-ATTR:kernel_id": "",
        "OS-EXT-SRV-ATTR:launch_index": 0,
        "OS-EXT-SRV-ATTR:ramdisk_id": "",
        "OS-EXT-SRV-ATTR:reservation_id": "r-iffothgx",
        "OS-EXT-SRV-ATTR:root_device_name": "/dev/sda",
        "OS-EXT-SRV-ATTR:user_data": "IyEvYmluL2Jhc2gKL2Jpbi9zdQplY2hvICJJIGFtIGluIHlvdSEiCg==",
        "OS-EXT-STS:power_state": 1,
        "OS-EXT-STS:task_state": 'null',
        "OS-EXT-STS:vm_state": "active",
        "OS-SRV-USG:launched_at": "2017-02-14T19:24:43.891568",
        "OS-SRV-USG:terminated_at": 'null',
        "accessIPv4": "1.2.3.4",
        "accessIPv6": "80fe::",
        "hostId": "2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6",
        "host_status": "UP",
        "id": "server-1",
        "metadata": {"My Server Name": "Apache1"},
        "name": "new-server-test",
        "status": "ACTIVE",
        "tags": [],
        "tenant_id": "6f70656e737461636b20342065766572",
        "updated": "2017-02-14T19:24:43Z",
        "user_id": "fake",
    }
]

# Example response from - https://developer.openstack.org/api-ref/compute/#list-servers-detailed
# ID and server-name values have been changed for test readability
MOCK_NOVA_SERVERS = [
    {
        "OS-DCF:diskConfig": "AUTO",
        "OS-EXT-AZ:availability_zone": "nova",
        "OS-EXT-SRV-ATTR:host": "compute",
        "OS-EXT-SRV-ATTR:hostname": "server-1",
        "OS-EXT-SRV-ATTR:hypervisor_hostname": "fake-mini",
        "OS-EXT-SRV-ATTR:instance_name": "instance-00000001",
        "OS-EXT-SRV-ATTR:kernel_id": "",
        "OS-EXT-SRV-ATTR:launch_index": 0,
        "OS-EXT-SRV-ATTR:ramdisk_id": "",
        "OS-EXT-SRV-ATTR:reservation_id": "r-iffothgx",
        "OS-EXT-SRV-ATTR:root_device_name": "/dev/sda",
        "OS-EXT-SRV-ATTR:user_data": "IyEvYmluL2Jhc2gKL2Jpbi9zdQplY2hvICJJIGFtIGluIHlvdSEiCg==",
        "OS-EXT-STS:power_state": 1,
        "OS-EXT-STS:task_state": 'null',
        "OS-EXT-STS:vm_state": "active",
        "OS-SRV-USG:launched_at": "2017-02-14T19:24:43.891568",
        "OS-SRV-USG:terminated_at": 'null',
        "accessIPv4": "1.2.3.4",
        "accessIPv6": "80fe::",
        "hostId": "2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6",
        "host_status": "UP",
        "id": "server-1",
        "metadata": {"My Server Name": "Apache1"},
        "name": "new-server-test",
        "status": "DELETED",
        "tags": [],
        "tenant_id": "6f70656e737461636b20342065766572",
        "updated": "2017-02-14T19:24:43Z",
        "user_id": "fake",
    },
    {
        "OS-DCF:diskConfig": "AUTO",
        "OS-EXT-AZ:availability_zone": "nova",
        "OS-EXT-SRV-ATTR:host": "compute",
        "OS-EXT-SRV-ATTR:hostname": "server-2",
        "OS-EXT-SRV-ATTR:hypervisor_hostname": "fake-mini",
        "OS-EXT-SRV-ATTR:instance_name": "instance-00000001",
        "OS-EXT-SRV-ATTR:kernel_id": "",
        "OS-EXT-SRV-ATTR:launch_index": 0,
        "OS-EXT-SRV-ATTR:ramdisk_id": "",
        "OS-EXT-SRV-ATTR:reservation_id": "r-iffothgx",
        "OS-EXT-SRV-ATTR:root_device_name": "/dev/sda",
        "OS-EXT-SRV-ATTR:user_data": "IyEvYmluL2Jhc2gKL2Jpbi9zdQplY2hvICJJIGFtIGluIHlvdSEiCg==",
        "OS-EXT-STS:power_state": 1,
        "OS-EXT-STS:task_state": 'null',
        "OS-EXT-STS:vm_state": "active",
        "OS-SRV-USG:launched_at": "2017-02-14T19:24:43.891568",
        "OS-SRV-USG:terminated_at": 'null',
        "accessIPv4": "1.2.3.4",
        "accessIPv6": "80fe::",
        "hostId": "2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6",
        "host_status": "UP",
        "id": "server_newly_added",
        "metadata": {"My Server Name": "Apache1"},
        "name": "newly_added_server",
        "status": "ACTIVE",
        "tags": [],
        "tenant_id": "6f70656e737461636b20342065766572",
        "updated": "2017-02-14T19:24:43Z",
        "user_id": "fake",
    },
]

EXAMPLE_GET_FLAVORS_DETAIL_RETURN_VALUE = [
    {'id': u'10', 'disk': 10, 'vcpus': 2, 'ram': 1024, 'OS-FLV-EXT-DATA:ephemeral': 0, 'swap': 0},
    {
        'id': u'625c2e4b-0a1f-4236-bb67-5ceee1a766e5',
        'disk': 48,
        'vcpus': 8,
        'ram': 5934,
        'OS-FLV-EXT-DATA:ephemeral': 0,
        'swap': 0,
    },
]

EXAMPLE_GET_OS_AGGREGATES_RETURN_VALUE = [{'hosts': ["compute"], 'name': "name", 'availability_zone': "london"}]

EXAMPLE_GET_OS_HYPERVISORS_RETURN_VALUE = [
    {
        "cpu_info": {
            "arch": "x86_64",
            "model": "Nehalem",
            "vendor": "Intel",
            "features": ["pge", "clflush"],
            "topology": {"cores": 1, "threads": 1, "sockets": 4},
        },
        "current_workload": 0,
        "status": "enabled",
        "state": "up",
        "disk_available_least": 0,
        "host_ip": "1.1.1.1",
        "free_disk_gb": 1028,
        "free_ram_mb": 7680,
        "hypervisor_hostname": "host1",
        "hypervisor_type": "fake",
        "hypervisor_version": 1000,
        "id": 2,
        "local_gb": 1028,
        "local_gb_used": 0,
        "memory_mb": 8192,
        "memory_mb_used": 512,
        "running_vms": 0,
        "service": {"host": "host1", "id": 7, "disabled_reason": None},
        "vcpus": 2,
        "vcpus_used": 0,
    }
]

EXAMPLE_GET_PROJECT_LIMITS_RETURN_VALUE = {
    "maxImageMeta": 128,
    "maxPersonality": 5,
    "maxPersonalitySize": 10240,
    "maxSecurityGroupRules": 20,
    "maxSecurityGroups": 10,
    "maxServerMeta": 128,
    "maxTotalCores": 20,
    "maxTotalFloatingIps": 10,
    "maxTotalInstances": 10,
    "maxTotalKeypairs": 100,
    "maxTotalRAMSize": 51200,
    "maxServerGroups": 10,
    "maxServerGroupMembers": 10,
    "totalCoresUsed": 0,
    "totalInstancesUsed": 0,
    "totalRAMUsed": 0,
    "totalSecurityGroupsUsed": 0,
    "totalFloatingIpsUsed": 1,
    "totalServerGroupsUsed": 0,
}

EXAMPLE_GET_NETWORKS_RETURN_VALUE = [
    {
        'id': u'2755452c-4fe8-4ba1-9b26-8898665b0958',
        'name': u'net2',
        'tenant_id': u'680031a39ce040e1b81289ea8c73fb11',
        'admin_state_up': True,
    }
]

DEFAULT_METRICS = [
    'openstack.controller',
    'openstack.nova.response_time',
    'openstack.nova.limits.max_image_meta',
    'openstack.nova.limits.max_personality',
    'openstack.nova.limits.max_personality_size',
    'openstack.nova.limits.max_security_group_rules',
    'openstack.nova.limits.max_security_groups',
    'openstack.nova.limits.max_server_group_members',
    'openstack.nova.limits.max_server_groups',
    'openstack.nova.limits.max_server_meta',
    'openstack.nova.limits.max_total_cores',
    'openstack.nova.limits.max_total_floating_ips',
    'openstack.nova.limits.max_total_instances',
    'openstack.nova.limits.max_total_keypairs',
    'openstack.nova.limits.max_total_ram_size',
    'openstack.nova.limits.total_cores_used',
    'openstack.nova.limits.total_floating_ips_used',
    'openstack.nova.limits.total_instances_used',
    'openstack.nova.limits.total_ram_used',
    'openstack.nova.limits.total_security_groups_used',
    'openstack.nova.limits.total_server_groups_used',
    'openstack.nova.quota_set.cores',
    'openstack.nova.quota_set.fixed_ips',
    'openstack.nova.quota_set.floating_ips',
    'openstack.nova.quota_set.injected_file_content_bytes',
    'openstack.nova.quota_set.injected_file_path_bytes',
    'openstack.nova.quota_set.injected_files',
    'openstack.nova.quota_set.instances',
    'openstack.nova.quota_set.key_pairs',
    'openstack.nova.quota_set.metadata_items',
    'openstack.nova.quota_set.ram',
    'openstack.nova.quota_set.security_group_rules',
    'openstack.nova.quota_set.security_groups',
    'openstack.nova.quota_set.server_group_members',
    'openstack.nova.quota_set.server_groups',
    'openstack.neutron.response_time',
    'openstack.neutron.quotas.floatingip',
    'openstack.neutron.quotas.network',
    'openstack.neutron.quotas.port',
    'openstack.neutron.quotas.rbac_policy',
    'openstack.neutron.quotas.router',
    'openstack.neutron.quotas.security_group',
    'openstack.neutron.quotas.security_group_rule',
    'openstack.neutron.quotas.subnet',
    'openstack.neutron.quotas.subnetpool',
    'openstack.nova.flavor.disk',
    'openstack.nova.flavor.os_flv_ext_data:ephemeral',
    'openstack.nova.flavor.ram',
    'openstack.nova.flavor.rxtx_factor',
    'openstack.nova.flavor.vcpus',
]


def _get_microversion_path(headers):
    nova_microversion_header = headers.get('X-OpenStack-Nova-API-Version')
    ironic_microversion_header = headers.get('X-OpenStack-Ironic-API-Version')

    nova_microversion = nova_microversion_header if nova_microversion_header is not None else "default"
    ironic_microversion = ironic_microversion_header if ironic_microversion_header is not None else "default"
    microversion_path = 'nova-{}-ironic-{}'.format(nova_microversion, ironic_microversion)
    return microversion_path


class MockHttp:
    def __init__(self, host, **kwargs):
        self._host = host
        self._exceptions = kwargs.get('exceptions')
        self._defaults = kwargs.get('defaults')
        self._replace = kwargs.get('replace')

    def get(self, url, *args, **kwargs):
        parsed_url = urlparse(url)
        path_and_args = parsed_url.path + "?" + parsed_url.query if parsed_url.query else parsed_url.path
        path_parts = path_and_args.split('/')
        microversion_path = _get_microversion_path(kwargs['headers'])
        subpath = os.path.join(
            *path_parts,
        )
        if self._exceptions and subpath in self._exceptions:
            raise self._exceptions[subpath]
        elif self._defaults and subpath in self._defaults:
            return self._defaults[subpath]
        else:
            file_path = os.path.join(
                get_here(),
                'fixtures',
                self._host,
                microversion_path,
                subpath,
                'get.json',
            )
            response = MockResponse(file_path=file_path, status_code=200).json()
            if self._replace and subpath in self._replace:
                response = self._replace[subpath](response)
            return MockResponse(json_data=response, status_code=200)

    def post(self, url, *args, **kwargs):
        parsed_url = urlparse(url)
        path_and_args = parsed_url.path + "?" + parsed_url.query if parsed_url.query else parsed_url.path
        path_parts = path_and_args.split('/')
        microversion_path = _get_microversion_path(kwargs['headers'])
        subpath = os.path.join(
            *path_parts,
        )
        if self._exceptions and subpath in self._exceptions:
            return self._exceptions[subpath]
        elif self._defaults and subpath in self._defaults:
            return self._defaults[subpath]
        elif path_and_args == '/identity/v3/auth/tokens':
            data = json.loads(kwargs['data'])
            project_id = data.get('auth', {}).get('scope', {}).get('project', {}).get('id')
            if project_id:
                file_path = os.path.join(
                    get_here(),
                    'fixtures',
                    self._host,
                    microversion_path,
                    *path_parts,
                    f'project_{project_id}.json',
                )
                headers = {'X-Subject-Token': f'token_{project_id}'}
            else:
                domain_id = data.get('auth', {}).get('scope', {}).get('domain', {}).get('id')
                if domain_id:
                    file_path = os.path.join(
                        get_here(),
                        'fixtures',
                        self._host,
                        microversion_path,
                        *path_parts,
                        f'domain_{domain_id}.json',
                    )
                    headers = {'X-Subject-Token': f'token_{domain_id}'}
                else:
                    file_path = os.path.join(
                        get_here(),
                        'fixtures',
                        self._host,
                        microversion_path,
                        *path_parts,
                        'unscoped.json',
                    )
                    headers = {'X-Subject-Token': 'token_test1234'}
        else:
            file_path = os.path.join(
                get_here(),
                'fixtures',
                self._host,
                microversion_path,
                subpath,
            )
        response = MockResponse(file_path=file_path, status_code=200).json()
        if self._replace and subpath in self._replace:
            response = self._replace[subpath](response)
        return MockResponse(json_data=response, status_code=200, headers=headers)
