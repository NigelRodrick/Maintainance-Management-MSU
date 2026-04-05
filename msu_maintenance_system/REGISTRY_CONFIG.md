# Container Registry Configuration

GitHub Packages Setup:
1. Enable packages in repository settings
2. Configure permissions for registry access
3. Set up automated image tagging

Registry URL: ghcr.io/maintenance/msu-maintenance-system
Image Tags: latest, {git-sha}

Push Commands:
docker build -t ghcr.io/maintenance/msu-maintenance-system:latest .
docker push ghcr.io/maintenance/msu-maintenance-system:latest
