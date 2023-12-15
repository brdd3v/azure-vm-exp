"""An Azure RM Python Pulumi program"""

import os
import pulumi
import pulumi_tls as tls
from pulumi_azure_native import (
    compute,
    network,
    resources
)


private_key_filename = "private_key.pem"

def write_file(content):
    with open(private_key_filename, "w") as f:
        f.write(content)
    os.chmod(private_key_filename, 0o600)

ssh_key = tls.PrivateKey("ssh_key",
    algorithm="RSA",
    rsa_bits=4096
)

ssh_key.private_key_pem.apply(lambda c: write_file(c))

resource_group = resources.ResourceGroup("rg",
    resource_group_name="resource-group-exp",
    location="Germany West Central"
)

virtual_network = network.VirtualNetwork("vnet",
    virtual_network_name="vnet-exp",
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
    resource_group_name=resource_group.name,
    location=resource_group.location
)

subnet = network.Subnet("subnet",
    name="subnet-exp",
    resource_group_name=resource_group.name,
    virtual_network_name=virtual_network.name,
    address_prefixes=["10.0.5.0/24"]
)

public_ip = network.PublicIPAddress("public_ip",
    public_ip_address_name="public-ip-exp",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_allocation_method="Static"
)

security_group = network.NetworkSecurityGroup("sg",
    network_security_group_name="security-group-exp",
    resource_group_name=resource_group.name,
    location=resource_group.location
)

sgr_http = network.SecurityRule("sgr_http",
    name="http",
    priority=100,
    direction="Inbound",
    access="Allow",
    protocol="Tcp",
    source_port_range="*",
    destination_port_range="80",
    source_address_prefix="*",
    destination_address_prefix="*",
    resource_group_name=resource_group.name,
    network_security_group_name=security_group.name
)

sgr_ssh = network.SecurityRule("sgr_ssh",
    name="ssh",
    priority=101,
    direction="Inbound",
    access="Allow",
    protocol="Tcp",
    source_port_range="*",
    destination_port_range="22",
    source_address_prefix="*",
    destination_address_prefix="*",
    resource_group_name=resource_group.name,
    network_security_group_name=security_group.name
)

sgr_out = network.SecurityRule("sgr_out",
    name="out",
    priority=102,
    direction="Outbound",
    access="Allow",
    protocol="Tcp",
    source_port_range="*",
    destination_port_range="*",
    source_address_prefix="*",
    destination_address_prefix="*",
    resource_group_name=resource_group.name,
    network_security_group_name=security_group.name
)

network_interface = network.NetworkInterface("ni",
    network_interface_name="network-interface-exp",
    resource_group_name=resource_group.name,
    location=resource_group.location,

    ip_configurations=[
        network.NetworkInterfaceIPConfigurationArgs(
            name="ni-ip-config-exp",
            subnet=network.SubnetArgs(
                id=subnet.id
            ),
            private_ip_allocation_method="Dynamic",
            public_ip_address=network.PublicIPAddressArgs(
                id=public_ip.id
            )
        )
    ],
    network_security_group=network.NetworkSecurityGroupArgs(
        id=security_group.id
    )
)

virtual_machine = compute.VirtualMachine("vm",
    vm_name="linux-vm-exp",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_B1s"
    ),
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[
            compute.NetworkInterfaceReferenceArgs(
                id=network_interface.id
            )
        ]
    ),
    storage_profile=compute.StorageProfileArgs(
        image_reference=compute.ImageReferenceArgs(
            publisher = "Canonical",
            offer="0001-com-ubuntu-server-jammy",
            sku="22_04-lts",
            version="latest"
        ),
        os_disk=compute.OSDiskArgs(
            caching="ReadWrite",
            create_option="FromImage",
            managed_disk=compute.ManagedDiskParametersArgs(
                storage_account_type="Standard_LRS"
            )
        )
    ),
    os_profile=compute.OSProfileArgs(
        admin_username="adminuser",
        computer_name="linux-vm-exp",
        linux_configuration=compute.LinuxConfigurationArgs(
            ssh=compute.SshConfigurationArgs(
                public_keys=[
                    compute.SshPublicKeyArgs(
                        key_data=ssh_key.public_key_openssh,
                        path="/home/adminuser/.ssh/authorized_keys"
                    )
                ]
            )
        )
    )
)

vm_extension = compute.VirtualMachineExtension("vm_ext",
    vm_extension_name="vm-extension-exp",
    resource_group_name=resource_group.name,
    vm_name=virtual_machine.name,
    type="CustomScript",
    publisher="Microsoft.Azure.Extensions",
    type_handler_version="2.1",
    settings={
        "commandToExecute": "apt-get -y update && apt-get install -y apache2"
    }
)

pulumi.export("public_ip", public_ip.ip_address)
