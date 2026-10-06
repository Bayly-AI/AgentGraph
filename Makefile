.PHONY: install test test-pre-deploy test-post-deploy

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -v

test-pre-deploy:
	python3 -m pytest -v --cov=agentgraph --cov-report=xml

test-post-deploy:
	python3 -c "import agentgraph; print('AgentGraph post-deploy check OK')"
