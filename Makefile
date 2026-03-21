.PHONY: prep_for_tagging
## Prepare for tagging (update lockfile/requirements, run pre-commit/deptry/vulture)
prep_for_tagging:
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv sync --locked
	@uv lock
	@uv export --format requirements-txt > requirements.txt
	@echo "🚀 Running pre-commit"
	@uv run pre-commit autoupdate
	@uv run pre-commit run --all-files
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .
	@echo "🚀 Checking for dead code: Running Vulture"
	@uv run vulture ./src

.PHONY: lint
## Lint code using Ruff
	@uv run ruff lint

.PHONY: cleanup_git
## List all local branches in a temporary file. Afterwards remove all branches from file.
cleanup_git:
	@echo "*****************************************************************************"
	@echo ">> Creating list of all merged branches without current, master or develop"
	@echo ">> Will fail if no branches are to be deleted"
	@echo "*****************************************************************************"

	@git branch --merged | grep -iv "master\|develop\|*" >/tmp/merged-branches
	@echo ">> Edit list so that it only contains branches to be deleted, then save."
	@echo ">> Hit <CTRL> + C to cancel."
	@vi /tmp/merged-branches && xargs git branch -d </tmp/merged-branches

.PHONY: update_docs
## Update the documentation
update_docs:
	sphinx-apidoc.exe --force --output-dir ./docs/source ./src
	sphinx-build -b html docs/source/ docs/build/

.PHONY: install
## Install for production
install:
	@echo "Creating virtual environment using uv"
	@uv sync
	@uv lock --locked
	@echo "Setting up pre-commit"
	@uv run pre-commit install
	@uv run pre-commit autoupdate
	@uv run pre-commit run --all-files
	@echo ">> Done!"

.PHONY: clean
## Delete all temporary files
clean:
	rm -rf build
	rm -rf dist


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

.PHONY: help
# Based on <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
