# syntax=docker/dockerfile:1
FROM python:3.12-slim

# WHY a container at all?
# So that "it works on my machine" is never a question a reviewer or
# recruiter has to ask. `docker compose up` reproduces the exact
# environment this repository was built and benchmarked against.

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

# Default action: run the comparison benchmark with a modest tick
# count so the container is useful out of the box without needing
# arguments.
CMD ["python", "benchmarks/compare.py", "200000", "1000"]
