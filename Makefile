SOURCE_FILES=$(shell find . -name '*.py' -not -path **/.venv/*)
STANFORD_MODEL := stanford-postagger-full-2017-06-09

clean/models/stanford:
	rm -rf $(STANFORD_MODEL)
	rm $(STANFORD_MODEL).zip

models/stanford:
	wget https://nlp.stanford.edu/software/$(STANFORD_MODEL).zip
	unzip $(STANFORD_MODEL).zip
	mkdir stanford-models
	mv $(STANFORD_MODEL)/stanford-postagger.jar $(STANFORD_MODEL)/models/spanish.tagger stanford-models
	rm -rf $(STANFORD_MODEL) && rm $(STANFORD_MODEL).zip

fmt:
	$(PIPENV_RUN) isort src
	$(PIPENV_RUN) black $(SOURCE_FILES)

train:
	MODELS_PATH=stanford-models PYTHONPATH=src $(PIPENV_RUN) python training/main.py