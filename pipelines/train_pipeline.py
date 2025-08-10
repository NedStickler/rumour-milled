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
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.inputs import TrainingInput
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid
import os


def create_pipeline():
    load_dotenv()
    sess = sagemaker.Session()
    role = os.environ.get("SM_EXEC_ROLE")

    run_id = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}-{uuid.uuid4().hex[:6]}"
    sagemaker_run_id = ParameterString("RunId", default_value=run_id)
    bucket = ParameterString("Bucket", default_value="rumour-milled")
    table = ParameterString("DynamoDBTable", default_value="Headlines")
    epochs = ParameterInteger("Epochs", default_value=100)
    lr = ParameterFloat("LR", default_value=0.001)
    batch_size = ParameterInteger("BatchSize", default_value=32)

    run_root = Join(on="", values=["s3://", bucket, "/runs/", sagemaker_run_id, "/"])
    input_uri = Join(on="", values=[run_root, "input/"])
    output_uri = Join(on="", values=[run_root, "output/"])

    processor = PyTorchProcessor(
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
    )

    step_process = ProcessingStep(
        name="ProcessHeadlines",
        processor=processor,
        code="services/processor/job.py",
        job_arguments=["--fake-size", "128", "--real-size", "128"],
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
        entry_point="services/trainer/job.py",
        role=role,
        framework_version="2.3",
        py_version="py311",
        instance_type="ml.m5.xlarge",
        instance_count=1,
        hyperparameters={"epochs": epochs, "lr": lr, "batch_size": batch_size},
        dependencies=["services/trainer/requirements.txt"],
        output_path=output_uri,
    )

    step_train = TrainingStep(
        name="TrainModel",
        estimator=estimator,
        inputs={
            "data": TrainingInput(
                step_process.properties.ProcessingOutputConfig.Outputs[
                    "input"
                ].S3Output.S3Uri
            )
        },
    )

    return Pipeline(
        name="RumourMilledPipeline",
        parameters=[sagemaker_run_id, bucket, table, epochs, lr, batch_size],
        steps=[step_process, step_train],
        sagemaker_session=sess,
    )


if __name__ == "__main__":
    load_dotenv()
    role = os.environ.get("SM_EXEC_ROLE")
    create_pipeline().upsert(role_arn=role)
