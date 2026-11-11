# Deployment Checklist

## Pre-Deployment Verification

### Code Quality
- [ ] All Python files compile without syntax errors
  ```bash
  python -m py_compile api.py graph.py main.py
  ```

- [ ] All pytest tests pass
  ```bash
  python -m pytest tests/ -v
  ```

- [ ] No hardcoded secrets in codebase
  ```bash
  grep -r "sk-" . --include="*.py" # Should return only .env references
  ```

- [ ] Verification script passes
  ```bash
  python verify_implementation.py
  ```

### Functionality Testing

#### Local FastAPI
- [ ] Start FastAPI server
  ```bash
  python -m uvicorn api:app --host 127.0.0.1 --port 8000
  ```

- [ ] Test health endpoint
  ```bash
  curl http://127.0.0.1:8000/health
  ```

- [ ] Test chat endpoint
  ```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello", "thread_id": "test-1"}'
  ```

- [ ] Access API documentation
  - http://127.0.0.1:8000/docs (Swagger UI)
  - http://127.0.0.1:8000/redoc (ReDoc)

- [ ] Test conversation continuity
  - Send 2+ messages with same thread_id
  - Verify context is preserved

- [ ] Test thread isolation
  - Send messages with different thread_id
  - Verify no context leakage

#### CLI Testing
- [ ] CLI (main.py) still works
  ```bash
  # Press Ctrl+C after startup
  python main.py
  ```

#### Docker Testing
- [ ] Docker image builds successfully
  ```bash
  docker build -t company-chat-agent .
  ```

- [ ] Docker container runs
  ```bash
  docker run --rm -p 8080:8080 --env-file .env company-chat-agent
  ```

- [ ] Test health endpoint in container
  ```bash
  curl http://localhost:8080/health
  ```

- [ ] Test chat endpoint in container
  ```bash
  curl -X POST http://localhost:8080/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Test", "thread_id": "docker-test"}'
  ```

### Configuration Verification
- [ ] .env file exists with required variables
  ```bash
  cat .env | grep OPENAI_API_KEY
  ```

- [ ] Environment variables are not exposed in code
  - grep -r "sk-proj" . # Should find nothing in .py files
  - Only .env file should contain secrets

- [ ] Configuration loads correctly
  ```bash
  python -c "from config.settings import settings; settings.validate(); print('OK')"
  ```

### Documentation Review
- [ ] IMPLEMENTATION_REPORT.md reviewed
- [ ] QUICKSTART.md reviewed
- [ ] COMPLETION_SUMMARY.md reviewed
- [ ] COMMANDS_REFERENCE.md reviewed
- [ ] FINAL_REPORT.md reviewed

---

## Google Cloud Run Deployment

### Prerequisites
- [ ] Google Cloud Project created
- [ ] gcloud CLI installed and authenticated
  ```bash
  gcloud auth login
  gcloud config set project PROJECT-ID
  ```

- [ ] Cloud Run API enabled
  ```bash
  gcloud services enable run.googleapis.com
  ```

- [ ] Container Registry API enabled
  ```bash
  gcloud services enable containerregistry.googleapis.com
  ```

### Build & Push
- [ ] Container Registry configured
  ```bash
  gcloud auth configure-docker
  ```

- [ ] Docker image built locally (no errors)
  ```bash
  docker build -t gcr.io/PROJECT-ID/company-chat-agent:latest .
  ```

- [ ] Docker image pushed to Registry
  ```bash
  docker push gcr.io/PROJECT-ID/company-chat-agent:latest
  ```

- [ ] Verify image exists in Registry
  ```bash
  gcloud container images list --repository=gcr.io/PROJECT-ID
  ```

### Deploy to Cloud Run
- [ ] Environment variables prepared
  - OPENAI_API_KEY (set to actual value)
  - OPENAI_MODEL (default: gpt-3.5-turbo)

- [ ] Cloud Run deployment command ready
  ```bash
  gcloud run deploy company-chat-agent \
    --image gcr.io/PROJECT-ID/company-chat-agent:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars OPENAI_API_KEY=sk-...,OPENAI_MODEL=gpt-3.5-turbo \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300
  ```

- [ ] Deployment successful
  ```bash
  gcloud run services list
  ```

### Post-Deployment Testing
- [ ] Get Cloud Run service URL
  ```bash
  gcloud run services describe company-chat-agent --region us-central1 --format='value(status.url)'
  ```

- [ ] Test health endpoint
  ```bash
  curl $(gcloud run services describe company-chat-agent \
    --region us-central1 --format='value(status.url)')/health
  ```

- [ ] Test chat endpoint
  ```bash
  curl -X POST $(gcloud run services describe company-chat-agent \
    --region us-central1 --format='value(status.url)')/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello", "thread_id": "cloud-test"}'
  ```

- [ ] Verify health checks passing
  ```bash
  gcloud run services describe company-chat-agent --region us-central1
  # Check for "Health Checks: Passed"
  ```

- [ ] Check service logs
  ```bash
  gcloud run logs read company-chat-agent --region us-central1 --limit 50
  ```

### Configuration & Security
- [ ] Secret Manager configured (optional, for production)
  ```bash
  echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
  ```

- [ ] Service account has necessary permissions
  - Cloud Run Service Agent
  - Can access secrets (if using Secret Manager)

- [ ] Authentication configured
  - [ ] Public access (allow-unauthenticated)
  - [ ] Service-to-service auth (requires authentication)
  - [ ] Custom authentication (API key, OAuth2)

- [ ] CORS configured if needed
  - Update api.py with FastAPI CORS middleware
  - Configure allowed origins

### Monitoring & Logging
- [ ] Cloud Logging enabled
  ```bash
  gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=company-chat-agent"
  ```

- [ ] Cloud Monitoring configured
  - Set up dashboard
  - Create alerts for error rates
  - Create alerts for latency
  - Create alerts for memory usage

- [ ] Error tracking enabled
  - Use Cloud Error Reporting
  - Set up notifications

---

## Production Hardening Checklist

### Before Going Live
- [ ] API authentication implemented
  - [ ] API key validation middleware
  - [ ] Rate limiting per API key
  - [ ] Usage tracking

- [ ] Request validation
  - [ ] Message content validation
  - [ ] Thread ID ownership validation
  - [ ] Request size limits

- [ ] State persistence
  - [ ] PostgreSQL checkpointer configured (or alternative)
  - [ ] Database backups configured
  - [ ] State migration tested

- [ ] Error handling
  - [ ] No stack traces exposed
  - [ ] Proper error codes returned
  - [ ] Error logging to Cloud Logging

- [ ] Performance optimization
  - [ ] Response caching if applicable
  - [ ] Request timeout handling
  - [ ] LLM rate limiting

### Security Hardening
- [ ] HTTPS enforced
  - [ ] Custom domain configured (optional)
  - [ ] SSL certificate valid
  - [ ] Redirect HTTP → HTTPS

- [ ] Secrets management
  - [ ] Remove .env file from deployment
  - [ ] Use Google Secret Manager
  - [ ] Never log sensitive values

- [ ] Network security
  - [ ] VPC configuration (if needed)
  - [ ] Firewall rules (if needed)
  - [ ] DDoS protection (Cloud Armor optional)

- [ ] Audit logging
  - [ ] API calls logged
  - [ ] User actions logged
  - [ ] Security events logged

### Operations
- [ ] Automated backups
  - [ ] Database backups (if applicable)
  - [ ] Configuration backups
  - [ ] Regular restore testing

- [ ] Disaster recovery
  - [ ] Failover mechanism defined
  - [ ] RTO/RPO requirements met
  - [ ] Recovery procedures documented
  - [ ] Recovery procedures tested

- [ ] Monitoring alerts
  - [ ] High error rate alert
  - [ ] High latency alert
  - [ ] Resource exhaustion alert
  - [ ] Unauthorized access alert

---

## Rollback Procedure

If issues occur after deployment:

### Quick Rollback
```bash
# Deploy previous version
gcloud run deploy company-chat-agent \
  --image gcr.io/PROJECT-ID/company-chat-agent:previous-tag \
  --region us-central1

# Or disable service temporarily
gcloud run services update company-chat-agent \
  --no-allow-unauthenticated \
  --region us-central1
```

### Verify Rollback
```bash
# Check service is back to previous version
gcloud run services describe company-chat-agent --region us-central1

# Check logs for errors
gcloud run logs read company-chat-agent --region us-central1 --limit 20
```

---

## Post-Deployment Monitoring

### Daily Checks
- [ ] Service is running (green status)
- [ ] No spike in error rates
- [ ] Response times normal
- [ ] No security alerts

### Weekly Checks
- [ ] Review error logs
- [ ] Check cost trends
- [ ] Verify backups completed
- [ ] Update documentation

### Monthly Checks
- [ ] Performance review
- [ ] Security audit
- [ ] Backup restore test
- [ ] Disaster recovery test

---

## Sign-Off

- [ ] All pre-deployment checks completed
- [ ] All tests passing
- [ ] Documentation reviewed
- [ ] Deployment procedure tested
- [ ] Rollback procedure tested
- [ ] Stakeholders notified
- [ ] Deployment scheduled

**Deployment Ready:** YES / NO

**Date:** _______________  
**Deployed By:** _______________  
**Approved By:** _______________  
**Deployment Time:** _______________  
**Status:** SUCCESS / FAILED  
**Notes:** _______________

---

## Emergency Contacts

- **On-Call Engineer:** _______________
- **Team Lead:** _______________
- **Operations Manager:** _______________
- **Security Team:** _______________

---

For questions or issues:
1. Check IMPLEMENTATION_REPORT.md
2. Check COMMANDS_REFERENCE.md
3. Review Cloud Run documentation
4. Contact team lead
