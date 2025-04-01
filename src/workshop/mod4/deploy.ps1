# deploy.ps1
# Deploy to Azure Container Apps using Docker and ACR

Set-StrictMode -Version Latest
$startTime = Get-Date

# Login to Azure
az login

# Configurable variables
$RESOURCE_GROUP = "azureagent-api"
$LOCATION = "centralus"
$ACR_NAME = "azureagentapiacr"
$APP_NAME = "azureagentapi-app"
$IMAGE_NAME = "azureagentapi:latest"
$CONTAINER_ENV_NAME = "azureagent-env"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --name $ACR_NAME --sku Basic --resource-group $RESOURCE_GROUP --admin-enabled true

# Build and push Docker image to ACR
az acr build --registry $ACR_NAME --image $IMAGE_NAME .

# Get ACR login server
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query "loginServer" -o tsv

# Create Azure Container Apps environment
az containerapp env create `
  --name $CONTAINER_ENV_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

# Create Container App
az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $CONTAINER_ENV_NAME `
  --image "$ACR_LOGIN_SERVER/$IMAGE_NAME" `
  --registry-server "$ACR_LOGIN_SERVER" `
  --ingress external `
  --target-port 80 `
  --env-vars SAMPLE_ENV_VAR="hello-from-azure"

# Done!
$APP_URL = az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv
Write-Output "Deployment complete. Visit: https://$APP_URL"

$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "Total Running Time: $($duration.ToString("hh\:mm\:ss"))"
