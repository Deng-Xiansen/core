import itertools
import os

import pytest
from mock import MagicMock

from core.emulator.session import Session
from core.errors import CoreCommandError
from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceDependencies, ServiceManager

_PATH = os.path.abspath(os.path.dirname(__file__))
_SERVICES_PATH = os.path.join(_PATH, "myservices")

SERVICE_ONE = "MyService"
SERVICE_TWO = "MyService2"


class TestServices:
    def test_service_all_files(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        file_name = "myservice.sh"
        node = session.add_node(CoreNode)

        # when
        session.services.set_service_file(node.id, SERVICE_ONE, file_name, "# test")

        # then
        service = session.services.get_service(node.id, SERVICE_ONE)
        all_files = session.services.all_files(service)
        assert service
        assert all_files and len(all_files) == 1

    def test_service_all_configs(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        node = session.add_node(CoreNode)

        # when
        session.services.set_service(node.id, SERVICE_ONE)
        session.services.set_service(node.id, SERVICE_TWO)

        # then
        all_configs = session.services.all_configs()
        assert all_configs
        assert len(all_configs) == 2

    def test_service_add_services(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        node = session.add_node(CoreNode)
        total_service = len(node.services)

        # when
        session.services.add_services(node, node.type, [SERVICE_ONE, SERVICE_TWO])

        # then
        assert node.services
        assert len(node.services) == total_service + 2

    def test_service_file(self, request, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)
        file_name = my_service.configs[0]
        file_path = node.hostfilename(file_name)

        # when
        session.services.create_service_files(node, my_service)

        # then
        if not request.config.getoption("mock"):
            assert os.path.exists(file_path)

    def test_service_validate(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)

        # when
        status = session.services.validate_service(node, my_service)

        # then
        assert not status

    def test_service_validate_error(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_TWO)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)
        node.cmd = MagicMock(side_effect=CoreCommandError(-1, "invalid"))

        # when
        status = session.services.validate_service(node, my_service)

        # then
        assert status

    def test_service_startup(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)

        # when
        status = session.services.startup_service(node, my_service, wait=True)

        # then
        assert not status

    def test_service_startup_error(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_TWO)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)
        node.cmd = MagicMock(side_effect=CoreCommandError(-1, "invalid"))

        # when
        status = session.services.startup_service(node, my_service, wait=True)

        # then
        assert status

    def test_service_stop(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)

        # when
        status = session.services.stop_service(node, my_service)

        # then
        assert not status

    def test_service_stop_error(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_TWO)
        node = session.add_node(CoreNode)
        session.services.create_service_files(node, my_service)
        node.cmd = MagicMock(side_effect=CoreCommandError(-1, "invalid"))

        # when
        status = session.services.stop_service(node, my_service)

        # then
        assert status

    def test_service_custom_startup(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)

        # when
        session.services.set_service(node.id, my_service.name)
        custom_my_service = session.services.get_service(node.id, my_service.name)
        custom_my_service.startup = ("sh custom.sh",)

        # then
        assert my_service.startup != custom_my_service.startup

    def test_service_set_file(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node1 = session.add_node(CoreNode)
        node2 = session.add_node(CoreNode)
        file_name = my_service.configs[0]
        file_data1 = "# custom file one"
        file_data2 = "# custom file two"
        session.services.set_service_file(
            node1.id, my_service.name, file_name, file_data1
        )
        session.services.set_service_file(
            node2.id, my_service.name, file_name, file_data2
        )

        # when
        custom_service1 = session.services.get_service(node1.id, my_service.name)
        session.services.create_service_files(node1, custom_service1)
        custom_service2 = session.services.get_service(node2.id, my_service.name)
        session.services.create_service_files(node2, custom_service2)

    def test_service_import(self):
        """
        Test importing a custom service.
        """
        ServiceManager.add_services(_SERVICES_PATH)
        assert ServiceManager.get(SERVICE_ONE)
        assert ServiceManager.get(SERVICE_TWO)

    def test_service_setget(self, session: Session):
        # given
        ServiceManager.add_services(_SERVICES_PATH)
        my_service = ServiceManager.get(SERVICE_ONE)
        node = session.add_node(CoreNode)

        # when
        no_service = session.services.get_service(node.id, SERVICE_ONE)
        default_service = session.services.get_service(
            node.id, SERVICE_ONE, default_service=True
        )
        session.services.set_service(node.id, SERVICE_ONE)
        custom_service = session.services.get_service(
            node.id, SERVICE_ONE, default_service=True
        )

        # then
        assert no_service is None
        assert default_service == my_service
        assert custom_service and custom_service != my_service

    def test_services_dependencies(self):
        # given
        service_a = CoreService()
        service_a.name = "a"
        service_b = CoreService()
        service_b.name = "b"
        service_c = CoreService()
        service_c.name = "c"
        service_d = CoreService()
        service_d.name = "d"
        service_e = CoreService()
        service_e.name = "e"
        service_a.dependencies = (service_b.name,)
        service_b.dependencies = ()
        service_c.dependencies = (service_b.name, service_d.name)
        service_d.dependencies = ()
        service_e.dependencies = ()
        services = [service_a, service_b, service_c, service_d, service_e]

        # when
        results = []
        permutations = itertools.permutations(services)
        for permutation in permutations:
            permutation = list(permutation)
            result = ServiceDependencies(permutation).boot_order()
            results.append(result)

        # then
        for result in results:
            assert len(result) == len(services)

    def test_services_missing_dependency(self):
        # given
        service_a = CoreService()
        service_a.name = "a"
        service_b = CoreService()
        service_b.name = "b"
        service_c = CoreService()
        service_c.name = "c"
        service_a.dependencies = (service_b.name,)
        service_b.dependencies = (service_c.name,)
        service_c.dependencies = ("d",)
        services = [service_a, service_b, service_c]

        # when, then
        permutations = itertools.permutations(services)
        for permutation in permutations:
            permutation = list(permutation)
            with pytest.raises(ValueError):
                ServiceDependencies(permutation).boot_order()

    def test_services_dependencies_cycle(self):
        # given
        service_a = CoreService()
        service_a.name = "a"
        service_b = CoreService()
        service_b.name = "b"
        service_c = CoreService()
        service_c.name = "c"
        service_a.dependencies = (service_b.name,)
        service_b.dependencies = (service_c.name,)
        service_c.dependencies = (service_a.name,)
        services = [service_a, service_b, service_c]

        # when, then
        permutations = itertools.permutations(services)
        for permutation in permutations:
            permutation = list(permutation)
            with pytest.raises(ValueError):
                ServiceDependencies(permutation).boot_order()

    def test_services_common_dependency(self):
        # given
        service_a = CoreService()
        service_a.name = "a"
        service_b = CoreService()
        service_b.name = "b"
        service_c = CoreService()
        service_c.name = "c"
        service_b.dependencies = (service_a.name,)
        service_c.dependencies = (service_a.name, service_b.name)
        services = [service_a, service_b, service_c]

        # when
        results = []
        permutations = itertools.permutations(services)
        for permutation in permutations:
            permutation = list(permutation)
            result = ServiceDependencies(permutation).boot_order()
            results.append(result)

        # then
        for result in results:
            assert result == [service_a, service_b, service_c]
