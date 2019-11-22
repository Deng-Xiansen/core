"""
sdn.py defines services to start Open vSwitch and the Ryu SDN Controller.
"""

import re

from core.nodes import ipaddress
from core.services.coreservices import CoreService


class SdnService(CoreService):
    """
    Parent class for SDN services.
    """

    group = "SDN"

    @classmethod
    def generate_config(cls, node, filename):
        return ""


class OvsService(SdnService):
    name = "OvsService"
    executables = ("ovs-ofctl", "ovs-vsctl")
    group = "SDN"
    dirs = ("/etc/openvswitch", "/var/run/openvswitch", "/var/log/openvswitch")
    configs = ("OvsService.sh",)
    startup = ("sh OvsService.sh",)
    shutdown = ("killall ovs-vswitchd", "killall ovsdb-server")

    @classmethod
    def generate_config(cls, node, filename):
        # Check whether the node is running zebra
        has_zebra = 0
        for s in node.services:
            if s.name == "zebra":
                has_zebra = 1

        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated by OvsService (OvsService.py)\n"
        cfg += "/etc/init.d/openvswitch-switch start < /dev/null\n"
        cfg += "ovs-vsctl add-br ovsbr0 -- set Bridge ovsbr0 fail-mode=secure\n"
        cfg += "ifconfig ovsbr0 up\n"

        for ifc in node.netifs():
            if hasattr(ifc, "control") and ifc.control is True:
                continue
            ifnumstr = re.findall(r"\d+", ifc.name)
            ifnum = ifnumstr[0]

            # create virtual interfaces
            cfg += "ip link add rtr%s type veth peer name sw%s\n" % (ifnum, ifnum)
            cfg += "ifconfig rtr%s up\n" % ifnum
            cfg += "ifconfig sw%s up\n" % ifnum

            # remove ip address of eths because quagga/zebra will assign same IPs to rtr interfaces
            # or assign them manually to rtr interfaces if zebra is not running
            for ifcaddr in ifc.addrlist:
                addr = ifcaddr.split("/")[0]
                if ipaddress.is_ipv4_address(addr):
                    cfg += "ip addr del %s dev %s\n" % (ifcaddr, ifc.name)
                    if has_zebra == 0:
                        cfg += "ip addr add %s dev rtr%s\n" % (ifcaddr, ifnum)
                elif ipaddress.is_ipv6_address(addr):
                    cfg += "ip -6 addr del %s dev %s\n" % (ifcaddr, ifc.name)
                    if has_zebra == 0:
                        cfg += "ip -6 addr add %s dev rtr%s\n" % (ifcaddr, ifnum)
                else:
                    raise ValueError("invalid address: %s" % ifcaddr)

            # add interfaces to bridge
            cfg += "ovs-vsctl add-port ovsbr0 eth%s\n" % ifnum
            cfg += "ovs-vsctl add-port ovsbr0 sw%s\n" % ifnum

        # Add rule for default controller if there is one local (even if the controller is not local, it finds it)
        cfg += "ovs-vsctl set-controller ovsbr0 tcp:127.0.0.1:6633\n"

        # Setup default flows
        portnum = 1
        for ifc in node.netifs():
            if hasattr(ifc, "control") and ifc.control is True:
                continue
            cfg += (
                "ovs-ofctl add-flow ovsbr0 priority=1000,in_port=%d,action=output:%d\n"
                % (portnum, portnum + 1)
            )
            cfg += (
                "ovs-ofctl add-flow ovsbr0 priority=1000,in_port=%d,action=output:%d\n"
                % (portnum + 1, portnum)
            )
            portnum += 2

        return cfg


class RyuService(SdnService):
    name = "ryuService"
    executables = ("ryu-manager",)
    group = "SDN"
    dirs = ()
    configs = ("ryuService.sh",)
    startup = ("sh ryuService.sh",)
    shutdown = ("killall ryu-manager",)

    @classmethod
    def generate_config(cls, node, filename):
        """
        Return a string that will be written to filename, or sent to the
        GUI for user customization.
        """
        cfg = "#!/bin/sh\n"
        cfg += "# auto-generated by ryuService (ryuService.py)\n"
        cfg += (
            "ryu-manager --observe-links ryu.app.ofctl_rest ryu.app.rest_topology &\n"
        )
        return cfg
