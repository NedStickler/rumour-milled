from datetime import datetime, timezone
import os, uuid
import sagemaker
from sagemaker.pytorch import PyTorch


def handler(event, context):
    detail = event.get("detail", {})
    if detail.get("lastStatus") != "STOPPED":
        return {"skipped": True, "reason": "not_stopped"}
    for container in detail.get("containers", []):
        if "exitCode" in container and container["exitCode"] != 0:
            return {"skipped": True, "reason": "non_zero_exit"}
    
    session = sagemaker.Session()
    role = os.environ["SM_EXEC_ROLE"]
    run_id = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}-{uuid.uuid4().hex[:6]}"


    estimator = PyTorch(
        job_name=f"rumour-milled-train-{run_id}",
        entry_point="job.py",
        source_dir="services/trainer/",
        role=role,
        framework_version="2.7",
        py_version="py312",
        instance_type="ml.m5.xlarge",
        instance_count=1,
        hyperparameters={
            "run-id": run_id,
            "epochs": 1000,
            "lr": 0.001,
            "batch-size": 64,
            "real-size": 2048,
            "fake-size": 2048,
        },
        dependencies=["dist/rumour_milled-0.1.0-py3-none-any.whl"],
        output_path=f"s3://rumour-milled/runs/{run_id}/output/",
        sagemaker_session=session,
    )
    estimator.fit(wait=False, logs=False)
    return {"ok": True, "job_name": estimator.latest_training_job.name}