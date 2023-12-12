// main.bicep

targetScope = 'subscription'

param adminUsername string = 'adminuser'
param location string = 'germanywestcentral'
@secure()
param publicKey string


resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'resource-group-exp'
  location: location
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: resourceGroup
  params: {
    adminUsername: adminUsername
    location: location
    publicKey: publicKey
  }
}
