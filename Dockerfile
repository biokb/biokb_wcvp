FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /code
COPY src ./src/
COPY pyproject.toml README.md ./
RUN uv pip install --system .
RUN mkdir -p /root/.biokb/wcvp
CMD ["fastapi", "run","src/biokb_wcvp/api/main.py"]
