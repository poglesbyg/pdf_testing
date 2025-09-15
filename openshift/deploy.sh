#!/bin/bash

# OpenShift Deployment Script for PDF Tracker

PROJECT_NAME="pdf-tracker"
GIT_REPO="https://github.com/your-username/pdf-tracker.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PDF Tracker OpenShift Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged in to OpenShift${NC}"
    echo "Please login using: oc login <your-openshift-url>"
    exit 1
fi

# Create new project or switch to existing
echo -e "\n${YELLOW}Creating/switching to project ${PROJECT_NAME}...${NC}"
oc new-project ${PROJECT_NAME} 2>/dev/null || oc project ${PROJECT_NAME}

# Apply build configurations
echo -e "\n${YELLOW}Creating build configurations...${NC}"
oc apply -f build-config.yaml

# Apply backend deployment
echo -e "\n${YELLOW}Deploying backend...${NC}"
oc apply -f backend-deployment.yaml

# Apply frontend deployment
echo -e "\n${YELLOW}Deploying frontend...${NC}"
oc apply -f frontend-deployment.yaml

# Start builds
echo -e "\n${YELLOW}Starting builds...${NC}"
oc start-build pdf-tracker-backend-build --follow
oc start-build pdf-tracker-frontend-build --follow

# Wait for deployments to be ready
echo -e "\n${YELLOW}Waiting for deployments to be ready...${NC}"
oc rollout status deployment/pdf-tracker-backend
oc rollout status deployment/pdf-tracker-frontend

# Get route
ROUTE=$(oc get route pdf-tracker -o jsonpath='{.spec.host}')

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nApplication URL: https://${ROUTE}"
echo -e "\nAPI Documentation: https://${ROUTE}/docs"
echo -e "\nHealth Check: https://${ROUTE}/health"

echo -e "\n${YELLOW}Useful commands:${NC}"
echo "  View pods:        oc get pods"
echo "  View logs:        oc logs -f deployment/pdf-tracker-backend"
echo "  Scale deployment: oc scale deployment/pdf-tracker-frontend --replicas=3"
echo "  Delete all:       oc delete project ${PROJECT_NAME}"
