// resources.bicep

param adminUsername string
param location string
@secure()
param publicKey string


resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: 'vnet-exp'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' = {
  name: 'subnet-exp'
  parent: vnet
  properties: {
    addressPrefixes: [
      '10.0.5.0/24'
    ]
  }
}

resource public_ip 'Microsoft.Network/publicIPAddresses@2023-05-01' = {
  name: 'public-ip-exp'
  location: location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource sg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: 'security-group-exp'
  location: location
}

resource sgr_http 'Microsoft.Network/networkSecurityGroups/securityRules@2023-05-01' = {
  name: 'http'
  parent: sg
  properties: {
    priority: 100
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourcePortRange: '*'
    destinationPortRange: '80'
    sourceAddressPrefix: '*'
    destinationAddressPrefix: '*'
  }
}

resource sgr_ssh 'Microsoft.Network/networkSecurityGroups/securityRules@2023-05-01' = {
  name: 'ssh'
  parent: sg
  properties: {
    priority: 101
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourcePortRange: '*'
    destinationPortRange: '22'
    sourceAddressPrefix: '*'
    destinationAddressPrefix: '*'
  }
}

resource sgr_out 'Microsoft.Network/networkSecurityGroups/securityRules@2023-05-01' = {
  name: 'out'
  parent: sg
  properties: {
    priority: 102
    direction: 'Outbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: '*'
    destinationAddressPrefix: '*'
  }
}

resource ni 'Microsoft.Network/networkInterfaces@2023-05-01' = {
  name: 'network-interface-exp'
  location: location

  properties: {
    ipConfigurations: [
      {
        name: 'ni-ip-config-exp'
        properties: {
          subnet: {
            id: subnet.id
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: public_ip.id
          }
        }
      }
    ]
    networkSecurityGroup: {
      id: sg.id
    }
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-07-01' = {
  name: 'linux-vm-exp'
  location: location
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_B1s'
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: ni.id
        }
      ]
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts'
        version: 'latest'
      }
      osDisk: {
        caching: 'ReadWrite'
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
    }
    osProfile: {
      adminUsername: adminUsername
      computerName: 'linux-vm-exp'
      linuxConfiguration: {
        ssh: {
          publicKeys: [
            {
              keyData: publicKey
              path: '/home/${adminUsername}/.ssh/authorized_keys'
            }
          ]
        }
      }
    }
  }
}

resource vm_ext 'Microsoft.Compute/virtualMachines/extensions@2023-07-01' = {
  name: 'vm-extension-exp'
  location: location
  parent: vm
  properties: {
    type: 'CustomScript'
    publisher: 'Microsoft.Azure.Extensions'
    typeHandlerVersion: '2.1'
    settings: {
      commandToExecute : 'sudo apt-get -y update && sudo apt-get install -y apache2'
    }
  }
}
