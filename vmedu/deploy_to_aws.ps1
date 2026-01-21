# Deploy to AWS Script
# Usage: ./deploy_to_aws.ps1

$REGION = "us-east-1"
$REPO_NAME = "vmedu-attendance"
$ACCOUNT_ID = ""

# 1. Check Prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

if (!(Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed! Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

if (!(Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed! Please install it: https://aws.amazon.com/cli/"
    exit 1
}

# 2. Get Account ID
try {
    $ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
    if (-not $ACCOUNT_ID) { throw "No Account ID" }
    Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Green
} catch {
    Write-Error "Failed to get AWS Account ID. Please run 'aws configure' first."
    exit 1
}

# 3. Create ECR Repository (Idempotent)
Write-Host "Creating ECR Repository '$REPO_NAME'..." -ForegroundColor Cyan
aws ecr create-repository --repository-name $REPO_NAME --region $REGION --output text 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Repository created successfully." -ForegroundColor Green
} else {
    Write-Host "Repository might already exist (ignoring error)." -ForegroundColor Yellow
}

# 4. Login to ECR
Write-Host "Logging into ECR..." -ForegroundColor Cyan
$uri = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $uri

# 5. Build Docker Image
Write-Host "Building Docker Image..." -ForegroundColor Cyan
docker build -t $REPO_NAME .

# 6. Tag and Push
Write-Host "Pushing Image to ECR..." -ForegroundColor Cyan
$full_image_uri = "$uri/$REPO_NAME`:latest"
docker tag "$REPO_NAME`:latest" $full_image_uri
docker push $full_image_uri

Write-Host "---------------------------------------------------" -ForegroundColor Green
Write-Host "Deployment Artifact Pushed Successfully!" -ForegroundColor Green
Write-Host "Image URI: $full_image_uri" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to AWS App Runner Console: https://console.aws.amazon.com/apprunner/home?region=$REGION"
Write-Host "2. Create Service -> Source: Container Registry"
Write-Host "3. URI: $full_image_uri"
Write-Host "4. Configuration: Port 8000"
Write-Host "---------------------------------------------------" -ForegroundColor Green
