# deploy_update.ps1
param (
  [string]$ACR_NAME = "azureagentapiacr",
  [string]$IMAGE_NAME = "azureagentapi:latest",
  [string]$APP_NAME = "azureagentapi-app",
  [string]$RESOURCE_GROUP = "azureagent-api"
)

Write-Host "Building and pushing Docker image '$IMAGE_NAME' to ACR '$ACR_NAME'..."
az acr build --registry $ACR_NAME --image $IMAGE_NAME .

Write-Host "Restarting web app '$APP_NAME' to apply the update..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

Write-Output "Update complete. Visit: https://$APP_NAME.azurewebsites.net"
