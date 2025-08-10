import sagemaker
from sagemaker.workflow.parameters import (
    ParameterString,
    ParameterInteger,
    ParameterFloat,
)
from sagemaker.workflow.functions import Join
from sagemaker.pytorch.processing import PyTorchProcessor
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.processing import ProcessingOutput
from sagemaker.pytorch import PyTorch
from datetime import datetime, timezone
import uuid


def create_pipeline():
    sess = sagemaker.Session()
    role = sagemaker.get_execution_role()

    run_id = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}-{uuid.uuid4().hex[:6]}"
    bucket = ParameterString("Bucket", default_value="rumour-milled")
    table = ParameterString("DynamoDBTable", default_value="Headlines")
    epochs = ParameterInteger("Epochs", default_value=100)
    lr = ParameterFloat("LR", default_value=0.001)
    batch_size = ParameterInteger("BatchSize", default_value=32)

    run_root = Join(on="", values=["s3://", bucket, "/runs/", run_id, "/"])
    input_uri = Join(on="", values=[run_root, "input/"])
    output_uri = Join(on="", values=[run_root, "output/"])

    processor = PyTorchProcessor(
        framework_version="2.3",
        py_version="py312",
        role=role,
        instance_type="ml.g5.xlarge",
        instance_count=1,
    )

    step_process = ProcessingStep(
        name="ProcessHeadlines",
        processor=processor,
        code="job.py",
        source="services/processor/",
        job_arguments=[],
        inputs=[],
        outputs=[
            ProcessingOutput(
                output_name="input",
                source="/opt/ml/processing/train",
                destination=input_uri,
            )
        ],
    )

    estimator = PyTorch(
        entry_point="job.py",
        source="services/trainer/",
        role=role,
        framework_version="2.3",
        py_version="py312",
        instance_type="ml.m5.xlarge",
        instance_count=1,
        hyperparameters={"epochs": epochs, "lr": lr, "batch_size": batch_size},
        output_path=output_uri,
    )

    step_train = TrainingStep(
        name="RumourMilledPipeline",
        parameters=[run_id, bucket, table, epochs, lr, batch_size],
        steps=[step_process, step_train],
        sagemaker_session=sess,
    )


if __name__ == "__main__":
    create_pipeline().upsert()
