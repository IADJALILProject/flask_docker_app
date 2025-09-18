📘 README (ID 5) — Flask Docker App — Micro-service data/ML (CI, pytest, k8s, Prom/Graf)
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

📘 README (ID 6) — Projet Talend 2 — Module ETL packagé (JAR) prêt production
1) Objectifs

Module Talend packagé (.jar) avec scripts .bat/.ps1, log4j2, audit/rejects, orchestration Airflow/k8s CronJobs, monitoring.

2) Exécution
# Windows
run\Module_Extract.ps1 && run\Module_Load.ps1
# Linux
bash run/module_extract.sh && bash run/module_load.sh

3) Intégrations

Airflow: BashOperator/KubernetesPodOperator.

k8s CronJobs pour le scheduling.

Prometheus exporter (durées, rows, erreurs) + Grafana.

4) Audit & Qualité

Tables etl_audit, etl_rejects, KPI rejets, redéclenchement idempotent.

5) Sécurité

Contexts séparés, secrets externalisés, RBAC DB.

6) Troubleshooting

JAR exit code ≠ 0 → lire logs/ via log4j2.

Connexion DB → vérifier contexts/*.properties.
