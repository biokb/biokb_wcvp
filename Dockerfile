FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /code

# Copy code
COPY src ./src/
COPY pyproject.toml README.md ./

RUN pip install .

# Start fastapi server
CMD ["uvicorn", "src.biokb_wcvp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]