1) Objectifs

Exposer un modèle/logiciel data/ML via API Flask dockerisée, testée pytest, déployable Kubernetes, observable Prometheus/Grafana.

2) Endpoints & contrat

GET /health → 200 OK

POST /predict → {"prediction": ..., "proba": ...} (exemples de schémas dans README)

GET /metrics → exposition Prometheus

3) Démarrage rapide
docker build -t flask-ml:latest .
docker run -p 8000:8000 --env-file .env flask-ml:latest
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"x":[1,2,3]}'
pytest -q

4) CI/CD & déploiement

CI: GitHub Actions (lint + tests + build image).

Kubernetes: kubectl apply -f k8s/ (Deployment, Service, HPA), ServiceMonitor si Prometheus Operator.

5) Observabilité

/metrics (latence, taux d’erreur).

Dashboard Grafana fourni (dashboards/flask.json).

6) Sécurité

Rate limiting, CORS contrôlé, secrets .env, logs sans PII.

7) Troubleshooting

500 → vérifier logs uvicorn/gunicorn.

Timeout → ajuster readinessProbe & timeouts client.
