from sagemaker.pytorch import PyTorch
from datetime import datetime, timezone
from dotenv import load_dotenv
import sagemaker
import uuid
import os


def get_estimator():
    load_dotenv()
    session = sagemaker.Session()
    role = os.environ.get("SM_EXEC_ROLE")

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
            "epochs": 100,
            "lr": 0.001,
            "batch-size": 128,
            "real-size": 128,
            "fake-size": 128,
        },
        dependencies=["dist/rumour_milled-0.1.0-py3-none-any.whl"],
        output_path=f"s3://rumour-milled/runs/{run_id}/output/",
        sagemaker_session=session,
    )
    return estimator


if __name__ == "__main__":
    estimator = get_estimator()
    estimator.fit()
