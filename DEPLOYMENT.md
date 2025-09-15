# PDF Submission Tracker - Deployment Guide

## Overview

This guide covers deployment options for the PDF Submission Tracker application, including local development with Docker Compose and production deployment on OpenShift.

## Architecture

The application consists of:
- **Backend**: FastAPI Python application with SQLite database
- **Frontend**: React application with Material-UI
- **Nginx**: Reverse proxy for frontend and API routing

## Local Development with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Quick Start

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

3. Stop the containers:
```bash
docker-compose down
```

### Development Mode

For development with hot reload:

```bash
# Start backend
cd /path/to/project
uv run python api_server.py

# Start frontend (in another terminal)
cd frontend
npm install
npm start
```

## OpenShift Deployment

### Prerequisites
- OpenShift CLI (`oc`) installed
- Access to an OpenShift cluster
- Git repository with your code

### Deployment Steps

1. **Login to OpenShift:**
```bash
oc login <your-openshift-url>
```

2. **Update Git Repository:**
Edit `openshift/build-config.yaml` and update the Git repository URL:
```yaml
git:
  uri: https://github.com/YOUR-USERNAME/pdf-tracker.git
```

3. **Run Deployment Script:**
```bash
cd openshift
chmod +x deploy.sh
./deploy.sh
```

4. **Manual Deployment:**
If you prefer manual deployment:
```bash
# Create project
oc new-project pdf-tracker

# Apply configurations
oc apply -f build-config.yaml
oc apply -f backend-deployment.yaml
oc apply -f frontend-deployment.yaml

# Start builds
oc start-build pdf-tracker-backend-build
oc start-build pdf-tracker-frontend-build

# Check deployment status
oc get pods
oc get routes
```

### Configuration

#### Environment Variables

Backend environment variables:
- `DATABASE_PATH`: Path to SQLite database (default: `/app/data/submissions.db`)
- `PYTHONUNBUFFERED`: Set to `1` for real-time logging

Frontend environment variables:
- `REACT_APP_API_URL`: Backend API URL (default: `http://backend:8000`)

#### Persistent Storage

The backend uses a PersistentVolumeClaim for database storage:
- Size: 5Gi
- Access Mode: ReadWriteOnce

Adjust in `backend-deployment.yaml` if needed.

#### Scaling

Scale deployments:
```bash
# Scale frontend
oc scale deployment/pdf-tracker-frontend --replicas=3

# Scale backend
oc scale deployment/pdf-tracker-backend --replicas=2
```

### Monitoring

#### Health Checks
- Backend: `/health`
- Frontend: `/`

#### View Logs
```bash
# Backend logs
oc logs -f deployment/pdf-tracker-backend

# Frontend logs
oc logs -f deployment/pdf-tracker-frontend
```

#### Metrics
```bash
# Pod resource usage
oc adm top pods

# Check deployment status
oc describe deployment pdf-tracker-backend
```

## Production Considerations

### Security

1. **API Authentication:**
   - Implement JWT authentication
   - Add API key validation
   - Configure CORS properly

2. **HTTPS:**
   - OpenShift Route provides TLS termination
   - Ensure all traffic is HTTPS

3. **Environment Variables:**
   - Use OpenShift Secrets for sensitive data
   - Never commit secrets to Git

### Database

For production, consider:
- PostgreSQL instead of SQLite for better concurrency
- Regular backups
- Database replication

### Performance

1. **Caching:**
   - Implement Redis for caching
   - Add CDN for static assets

2. **Resource Limits:**
   - Adjust CPU/Memory limits based on load
   - Monitor and optimize as needed

### Backup and Recovery

1. **Database Backup:**
```bash
# Create backup
oc exec deployment/pdf-tracker-backend -- tar czf /tmp/backup.tar.gz /app/data
oc cp pdf-tracker-backend-<pod-id>:/tmp/backup.tar.gz ./backup.tar.gz
```

2. **Restore:**
```bash
# Restore backup
oc cp ./backup.tar.gz pdf-tracker-backend-<pod-id>:/tmp/backup.tar.gz
oc exec deployment/pdf-tracker-backend -- tar xzf /tmp/backup.tar.gz -C /
```

## Troubleshooting

### Common Issues

1. **Pods not starting:**
```bash
oc describe pod <pod-name>
oc logs <pod-name>
```

2. **Build failures:**
```bash
oc logs -f bc/pdf-tracker-backend-build
```

3. **Route not accessible:**
```bash
oc get routes
oc describe route pdf-tracker
```

4. **Database connection issues:**
- Check PVC is bound: `oc get pvc`
- Verify mount path in pod: `oc exec <pod> -- ls -la /app/data`

### Debug Mode

Enter pod shell for debugging:
```bash
oc exec -it <pod-name> -- /bin/sh
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to OpenShift

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install OpenShift CLI
        run: |
          wget https://downloads-openshift-console.apps.openshift.com/amd64/linux/oc.tar
          tar -xvf oc.tar
          sudo mv oc /usr/local/bin/
      
      - name: Login to OpenShift
        run: |
          oc login --token=${{ secrets.OPENSHIFT_TOKEN }} --server=${{ secrets.OPENSHIFT_SERVER }}
      
      - name: Deploy
        run: |
          oc project pdf-tracker
          oc start-build pdf-tracker-backend-build --follow
          oc start-build pdf-tracker-frontend-build --follow
```

## Support

For issues or questions:
1. Check application logs
2. Review OpenShift events: `oc get events`
3. Consult OpenShift documentation
4. Contact your OpenShift administrator
