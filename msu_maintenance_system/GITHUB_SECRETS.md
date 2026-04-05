# GitHub Repository Secrets Setup

Required Secrets:
1. GITHUB_TOKEN (auto-provided)
2. DB_PASSWORD - Database password
3. SECRET_KEY - Application secret key
4. DOCKER_REGISTRY_TOKEN - Container registry token

Setup Commands:
gh secret set DB_PASSWORD --body "YourStrong!Passw0rd"
gh secret set SECRET_KEY --body "your-32-character-secret-key"
gh secret set DOCKER_REGISTRY_TOKEN --body "ghp_xxxxxxxxxxxx"

Environment Protection:
- Production environment requires approval
- Staging environment auto-deploys
- Manual review for critical changes
