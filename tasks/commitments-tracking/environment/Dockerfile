FROM python:3.11-slim

WORKDIR /app

ENV WORKSPACE_STATE=/workspace/state.json

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
RUN pip install openai python-dotenv
RUN mkdir -p /workspace /logs/verifier

COPY services/ /app/services/
COPY seed.py /app/seed.py
COPY bin/slack /usr/local/bin/slack
COPY bin/tasks /usr/local/bin/tasks
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /usr/local/bin/slack /usr/local/bin/tasks /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["bash"]
