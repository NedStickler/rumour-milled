# rumour-milled
Detecting misinformation in news headlines.

## AWS Infrastructure

LocalStack for building and testing.

EventBridge Schedule -> ECS (Headline Scraper) -> Lambda (On Scrape Finish) -> Sagemaker (Retrain Models)

### Scheduler (EventBridge Schedule)

- Schedule (rm-dev-weekly-scrape)
    - `infra/eventbridge/scheduler/rm-dev-weekly-scrape.json`
- Role (rm-dev-scheduler-role)
    - `infra/iam/roles/rm-dev-scheduler-role/trust-policy.json`
    - `infra/iam/roles/rm-dev-scheduler-role/inline-policy.json`

### Headline Scraper (ECS)

- Scraper Image (rm-dev-scraper)
    - `services/scraper/*`
- Cluster Definition (rm-dev-ecs-cluster)
    - `infra/ecs/clusters/rm-dev-ecs-cluster.json`
- Task Definition (rm-dev-scraper-task)
    - `infra/ecs/tasks/rm-dev-scraper-task.json`
- Execution Role (rm-dev-ecs-exec-role)
    - `infra/iam/roles/rm-dev-ecs-exec-role/trust-policy.json`
    - `infra/iam/roles/rm-dev-ecs-exec-role/attach.json`
- Task Role (rm-dev-ecs-task-role)
    - `infra/iam/roles/rm-dev-ecs-task-role/trust-policy.json`
    - `infra/iam/roles/rm-dev-ecs-task-role/inline-policy.json`

### Scrape Finish (EventBridge Rule)

- Rule (rm-dev-scrape-finish-rule)
    - `infra/eventbridge/rules/rm-dev-scrape-finish-rule/rule-pattern.json`
    - `infra/eventbridge/rules/rm-dev-scrape-finish-rule/targets.json`

### Scrape Finish Handler (Lambda)

- Handler Function (rm-dev-lambda-scrape-finish-handler)
    - `services/scrape_finish_handler/*`
- Execution Role (rm-dev-lamda-scrape-finish-handler-exec-role)
    - `infra/iam/roles/rm-dev-scrape-finish-handler-exec-role/trust-policy.json`
    - `infra/iam/roles/rm-dev-scrape-finish-handler-exec-role/inline-policy.json`
    - `infra/iam/roles/rm-dev-scrape-finish-handler-exec-role/attach.json`

### Model Training (SageMaker)

- Training Function
    - `services/trainer/*`
- Execution Role (rm-dev-sagemaker-exec-role)
    - `infra/iam/roles/rm-dev-sagemaker-exec-role/trust-policy.json`
    - `infra/iam/role/rm-dev-sagemaker-exec-role/inline-policy.json`






