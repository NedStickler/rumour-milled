from sagemaker.workflow.pipeline import Pipeline
import sagemaker


if __name__ == "__main__":
    import boto3, json

    region = "eu-west-2"
    name = "RumourMilledPipeline"

    sm = boto3.client("sagemaker", region_name=region)

    # latest execution
    execs = sm.list_pipeline_executions(PipelineName=name, MaxResults=1)[
        "PipelineExecutionSummaries"
    ]
    exec_arn = execs[0]["PipelineExecutionArn"]

    steps = sm.list_pipeline_execution_steps(PipelineExecutionArn=exec_arn)[
        "PipelineExecutionSteps"
    ]
    print(json.dumps(steps, indent=2))

    # (optional) richer detail for each step
    for s in steps:
        d = sm.get_pipeline_execution_step(
            PipelineExecutionArn=exec_arn, StepName=s["StepName"]
        )
        print("\n==", s["StepName"], "==")
        print("Status:", d["StepStatus"])
        print("FailureReason:", d.get("FailureReason"))
