.PHONY: eval test

eval:
	python -m eval.run_eval

test:
	pytest -q

