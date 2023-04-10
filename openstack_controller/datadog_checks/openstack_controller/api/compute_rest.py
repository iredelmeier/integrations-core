# (C) Datadog, Inc. 2023-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import re


def convert_metric_name(name):
    return re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name).lower().replace("-", "_")


def _load_averages_from_uptime(uptime):
    """Parse u' 16:53:48 up 1 day, 21:34,  3 users,  load average: 0.04, 0.14, 0.19\n'"""
    uptime = uptime.strip()
    load_averages = uptime[uptime.find('load average:') :].split(':')[1].strip().split(',')
    load_averages = [float(load_avg) for load_avg in load_averages]
    return load_averages


class ComputeRest:
    def __init__(self, log, http, endpoint):
        self.log = log
        self.http = http
        self.endpoint = endpoint
        self.log.debug("compute endpoint: %s", endpoint)

    def get_response_time(self):
        response = self.http.get('{}'.format(self.endpoint))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        return response.elapsed.total_seconds() * 1000

    def get_limits(self, project_id):
        response = self.http.get('{}/limits?tenant_id={}'.format(self.endpoint, project_id))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        return {
            convert_metric_name(key): value
            for key, value in response.json()['limits']['absolute'].items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }

    def get_quota_set(self, project_id):
        response = self.http.get('{}/os-quota-sets/{}'.format(self.endpoint, project_id))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        quota_set = {
            'id': response.json()['quota_set']['id'],
            'metrics': {
                re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key).lower().replace("-", "_"): value
                for key, value in response.json()['quota_set'].items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            },
        }
        return quota_set

    def get_services(self):
        response = self.http.get('{}/os-services'.format(self.endpoint))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        services = []
        for service in response.json().get('services'):
            binary = service.get('binary').replace('-', '_')
            is_down = service.get('state') is not None and service.get('state') == 'down'
            is_enabled = service.get('status') == 'enabled'
            is_up = not (is_down and is_enabled)
            services.append(
                {
                    'binary': binary,
                    'is_up': is_up,
                    'host': service.get('host'),
                    'status': service.get('status'),
                    'service_id': service.get('id'),
                    'state': service.get('state'),
                }
            )
        return services

    def get_servers(self, project_id):
        response = self.http.get('{}/servers/detail?project_id={}'.format(self.endpoint, project_id))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        server_metrics = {}
        for server in response.json()['servers']:
            server_metrics[server['id']] = {
                'name': server['name'],
                'status': server['status'].lower(),
                'hypervisor_hostname': server['OS-EXT-SRV-ATTR:hypervisor_hostname'],
                'metrics': {},
            }
            flavor = server.get('flavor')
            if flavor:
                flavor_id = flavor.get('id')
                if flavor_id is not None:
                    flavor_metrics = self._get_flavor_id(flavor_id)
                    server_metrics[server['id']]['flavor_name'] = flavor_metrics[flavor_id]['name']
                    server_metrics[server['id']]['metrics'].update(
                        {
                            '{}.{}'.format(
                                'flavor',
                                re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key)
                                .lower()
                                .replace("-", "_"),
                            ): value
                            for key, value in flavor_metrics[flavor_id]['metrics'].items()
                            if isinstance(value, (int, float)) and not isinstance(value, bool)
                        }
                    )
                else:
                    server_metrics[server['id']]['flavor_name'] = flavor.get('original_name')
                    server_metrics[server['id']]['metrics'].update(
                        {
                            '{}.{}'.format(
                                'flavor',
                                re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key)
                                .lower()
                                .replace("-", "_"),
                            ): value
                            for key, value in flavor.items()
                            if isinstance(value, (int, float)) and not isinstance(value, bool)
                        }
                    )
            try:
                response = self.http.get('{}/servers/{}/diagnostics'.format(self.endpoint, server['id']))
                response.raise_for_status()
                self.log.debug("response: %s", response.json())
                disk_details = response.json().get('disk_details')
                if disk_details:
                    for disk_detail in disk_details:
                        server_metrics[server['id']]['metrics'].update(
                            {
                                '{}.{}'.format(
                                    'disk_details',
                                    re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key)
                                    .lower()
                                    .replace("-", "_"),
                                ): value
                                for key, value in disk_detail.items()
                                if isinstance(value, (int, float)) and not isinstance(value, bool)
                            }
                        )
                cpu_details = response.json().get('cpu_details')
                if cpu_details:
                    for cpu_detail in cpu_details:
                        server_metrics[server['id']]['metrics'].update(
                            {
                                '{}.{}'.format(
                                    'cpu_details',
                                    re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key)
                                    .lower()
                                    .replace("-", "_"),
                                ): value
                                for key, value in cpu_detail.items()
                                if isinstance(value, (int, float)) and not isinstance(value, bool)
                            }
                        )
                server_metrics[server['id']]['metrics'].update(
                    {
                        re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key)
                        .lower()
                        .replace("-", "_"): value
                        for key, value in response.json().items()
                        if isinstance(value, (int, float)) and not isinstance(value, bool)
                    }
                )
            except Exception as e:
                self.log.info(
                    "Could not query the server diagnostics endpoint for server %s, "
                    "perhaps it is a bare metal machine: %s",
                    server.get("id", None),
                    e,
                )
        return server_metrics

    def get_flavors(self):
        response = self.http.get('{}/flavors/detail'.format(self.endpoint))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        flavor_metrics = {}
        for flavor in response.json()['flavors']:
            flavor_metrics[flavor['id']] = {
                'name': flavor['name'],
                'metrics': {
                    re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key).lower().replace("-", "_"): value
                    for key, value in flavor.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                },
            }
        return flavor_metrics

    def _get_flavor_id(self, flavor_id):
        response = self.http.get('{}/flavors/{}'.format(self.endpoint, flavor_id))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        flavor_metrics = {}
        flavor = response.json()['flavor']
        flavor_metrics[flavor['id']] = {'name': flavor['name'], 'metrics': {}}
        for key, value in flavor.items():
            metric_key = re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key).lower().replace("-", "_")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                flavor_metrics[flavor['id']]['metrics'][metric_key] = value
            elif isinstance(value, str):
                try:
                    flavor_metrics[flavor['id']]['metrics'][metric_key] = int(value) if value else 0
                except ValueError:
                    pass
        return flavor_metrics

    def get_hypervisors(self):
        response = self.http.get('{}/os-hypervisors/detail?with_servers=true'.format(self.endpoint))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        hypervisors_detail_metrics = {}
        for hypervisor in response.json()['hypervisors']:
            hypervisors_detail_metrics[str(hypervisor['id'])] = {
                'name': hypervisor['hypervisor_hostname'],
                'state': hypervisor.get('state'),
                'type': hypervisor['hypervisor_type'],
                'status': hypervisor['status'],
                'metrics': {
                    re.sub(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', key).lower().replace("-", "_"): value
                    for key, value in hypervisor.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                },
            }
            uptime = hypervisor.get('uptime')
            load_averages = []
            if uptime:
                load_averages = _load_averages_from_uptime(uptime)
            else:
                try:
                    response_uptime = self.http.get(
                        '{}/os-hypervisors/{}/uptime'.format(self.endpoint, hypervisor['id'])
                    )
                    if 200 <= response_uptime.status_code < 300:
                        self.log.debug("response uptime: %s", response_uptime.json())
                        uptime = response_uptime.json().get('hypervisor', {}).get('uptime')
                        if uptime:
                            load_averages = _load_averages_from_uptime(uptime)
                except Exception as e:
                    self.log.info(
                        "Could not query the uptime for hypervisor %s, perhaps it is a bare metal: %s",
                        hypervisor.get('id'),
                        e,
                    )

            if load_averages and len(load_averages) == 3:
                for i, avg in enumerate([1, 5, 15]):
                    hypervisors_detail_metrics[str(hypervisor['id'])]['metrics']['load_{}'.format(avg)] = load_averages[
                        i
                    ]
        return hypervisors_detail_metrics

    def get_os_aggregates(self):
        response = self.http.get('{}/os-aggregates'.format(self.endpoint))
        response.raise_for_status()
        self.log.debug("response: %s", response.json())
        os_aggregates = {}
        for aggregate in response.json()['aggregates']:
            os_aggregates[str(aggregate['id'])] = {
                'name': aggregate['name'],
                'availability_zone': aggregate['availability_zone'],
                'hosts': aggregate['hosts'],
            }
        return os_aggregates
