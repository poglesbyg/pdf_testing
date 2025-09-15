# OpenShift Deployment Setup

## Current Status

Based on your OpenShift access, you have permissions to the `dept-barc` project. The deployment script has been updated to use this project.

## Prerequisites Before Deployment

### 1. Update Git Repository

The build configuration expects your code to be in a Git repository. Update the repository URL in `openshift/build-config.yaml`:

```yaml
git:
  uri: https://github.com//poglesbyg/pdf_testing.git  # <-- Update this
  ref: main
```

### 2. Push Your Code to Git

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com//poglesbyg/pdf_testing.git
git push -u origin main
```

### 3. Deploy to OpenShift

```bash
# Make sure you're logged in to OpenShift
oc login <your-openshift-url>

# Run the deployment
./openshift/deploy.sh
```

## Alternative: Local Development First

If you want to test locally before deploying to OpenShift:

### 1. Test Backend API

```bash
# Start the API server
uv run python api_server.py

# In another terminal, test the API
curl http://localhost:8000/health
```

### 2. Test Frontend

```bash
# Install frontend dependencies
cd frontend
npm install

# Start the development server
npm start

# Access at http://localhost:3000
```

### 3. Test with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000/docs
```

## Deployment Options

### Option 1: Deploy Without Building (Using Pre-built Images)

If you don't have a Git repository set up yet, you can:

1. Build Docker images locally
2. Push to OpenShift's internal registry
3. Deploy using those images

```bash
# Build locally
docker build -f backend.Dockerfile -t pdf-tracker-backend .
docker build -f frontend.Dockerfile -t pdf-tracker-frontend .

# Tag for OpenShift registry
docker tag pdf-tracker-backend <openshift-registry>/dept-barc/pdf-tracker-backend:latest
docker tag pdf-tracker-frontend <openshift-registry>/dept-barc/pdf-tracker-frontend:latest

# Push to OpenShift
docker push <openshift-registry>/dept-barc/pdf-tracker-backend:latest
docker push <openshift-registry>/dept-barc/pdf-tracker-frontend:latest
```

### Option 2: Deploy Backend Only First

Start with just the API to test:

```bash
# Deploy only backend
oc apply -f openshift/backend-deployment.yaml

# Expose the service
oc expose svc/pdf-tracker-backend

# Get the route
oc get route pdf-tracker-backend
```

## Troubleshooting

### If builds fail:
```bash
# Check build logs
oc logs -f bc/pdf-tracker-backend-build

# Check if ImageStreams exist
oc get is

# Check pods
oc get pods
```

### If deployments fail:
```bash
# Check deployment status
oc describe deployment pdf-tracker-backend

# Check events
oc get events --sort-by='.lastTimestamp'

# Check PVC
oc get pvc
```

## Next Steps

1. **Set up Git repository** - Required for OpenShift builds
2. **Test locally** - Verify everything works before deploying
3. **Deploy backend first** - Test API independently
4. **Deploy frontend** - Once backend is working
5. **Configure persistent storage** - Ensure database persists

## Notes

- The `dept-barc` project will be used instead of creating a new project
- All resources will be labeled with `app: pdf-tracker` for easy management
- The route will be accessible at the OpenShift-provided URL
- Database will use persistent storage (5Gi PVC)
