FROM public.ecr.aws/lambda/python:3.12

# Dependencies
COPY services/ecs_finish_handler services/ecs_finish_handler
COPY services/trainer services/trainer
COPY dist/rumour_milled-0.1.0-py3-none-any.whl dist/

RUN pip install --no-cache-dir -r services/ecs_finish_handler/requirements.txt

CMD ["services/ecs_finish_handler.job.handler"]