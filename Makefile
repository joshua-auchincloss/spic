cov:
		source ./env/bin/activate && \
		./scripts/test.sh && \
		./scripts/cov.sh
lint:
		black ./src && black ./tests \
		&& ruff check ./src
test-env:
		python3.10 -m virtualenv env && \
		source ./env/bin/activate && \
		pip install '.[dev,experimental,msgpack,core]'
