from sagemaker.workflow.pipeline import Pipeline
import sagemaker


if __name__ == "__main__":
    sess = sagemaker.Session()
    pipeline = Pipeline("RumourMilledPipeline", sagemaker_session=sess)
    pipeline.start()
