FROM python:3.12
WORKDIR /project_group_1
RUN pip install --no-cache-dir pdm
RUN pip install --no-cache-dir pdm uvicorn
RUN pip install cryptography
RUN pip install "fastapi[standard]"
COPY ./ /project_group_1 
COPY pyproject.toml pdm.lock /project_group_1/
# RUN pip install --no-lock --no-editable
RUN pip install /project_group_1
# CMD ["pdm", "run", "make_executable" ]
CMD ["fastapi", "run", "src/project_group_1/main.py", "--port", "81"]