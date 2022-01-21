# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tftokenizers']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx==4.1.2',
 'datasets>=1.17.0,<2.0.0',
 'myst-parser==0.15.2',
 'pydantic>=1.9.0,<2.0.0',
 'python-decouple>=3.5,<4.0',
 'readthedocs-sphinx-search==0.1.1',
 'recommonmark>=0.7.1,<0.8.0',
 'requests==2.26.0',
 'rich[jupyter]>=10.14.0,<11.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'sphinx-copybutton==0.4.0',
 'sphinx-markdown-tables==0.0.15',
 'sphinx-rtd-theme==1.0.0',
 'sphinxemoji>=0.2.0,<0.3.0',
 'sphinxext-opengraph==0.4.2',
 'tensorflow-datasets>=4.4.0,<5.0.0',
 'tensorflow-hub>=0.12.0,<0.13.0',
 'tensorflow-text==2.5.0',
 'tensorflow==2.5.2',
 'tf-sentencepiece>=0.1.92,<0.2.0',
 'tomlkit==0.7.2',
 'torch>=1.10.1,<2.0.0',
 'transformers>=4.15.0,<5.0.0',
 'unzip>=1.0.0,<2.0.0',
 'wget>=3.2,<4.0']

setup_kwargs = {
    'name': 'tftokenizers',
    'version': '0.1.2',
    'description': 'Use Huggingface Transformer and Tokenizers as Tensorflow Reusable SavedModels.',
    'long_description': '# TFtftransformers\nConverting Hugginface tokenizers to Tensorflow tokenizers. The main reason is to be able to bundle the tokenizer and model into one Reusable SavedModel.\n\n<a href="https://badge.fury.io/py/tftokenizers"><img src="https://badge.fury.io/py/tftokenizers.svg" alt="PyPI version" height="18"></a>\n---\n\n**Source Code**: <a href="https://github.com/Huggingface-Supporters/tftftransformers" target="_blank">https://github.com/Hugging-Face-Supporter/tftokenizers</a>\n\n---\n\n\n## Example\nThis is an example of how one can use Huggingface model and tokenizers bundled together as a [Reusable SavedModel](https://www.tensorflow.org/hub/reusable_saved_models) and yields the same result as using the model and tokenizer from Huggingface 🤗\n\n\n```python\nimport tensorflow as tf\nfrom tftokenizer import TFModel\nfrom tftokenizers import TFAutoTokenizer\nfrom transformers import TFAutoModel\n\n# Load base models from Huggingface\nmodel_name = "bert-base-cased"\nmodel = TFAutoModel.from_pretrained(model_name)\n\n# Load converted TF tokenizer\ntokenizer = TFAutoTokenizer(model_name)\n\n# Create a TF Reusable SavedModel\ncustom_model = TFModel(model=model, tokenizer=tokenizer)\n\n# Tokenizer and model can handle `tf.Tensors` or regular strings\ntf_string = tf.constant(["Hello from Tensorflow"])\ns1 = "SponGE bob SQuarePants is an avenger"\ns2 = "Huggingface to Tensorflow tokenizers"\ns3 = "Hello, world!"\n\noutput = custom_model(tf_string)\noutput = custom_model([s1, s2, s3])\n\n# You can also pass arguments, similar to Huggingface tokenizers\noutput = custom_model(\n    [s1, s2, s3],\n    max_length=512,\n    padding="max_length",\n)\nprint(output)\n\n# Save tokenizer\nsaved_name = "reusable_bert_tf"\ntf.saved_model.save(custom_model, saved_name)\n\n# # Load tokenizer\nreloaded_model = tf.saved_model.load(saved_name)\noutput = reloaded_model([s1, s2, s3])\nprint(output)\n```\n\n## `Setup`\n```bash\ngit clone https://github.com/Hugging-Face-Supporter/tftokenizers.git\ncd tftokenizers\npoetry install\npoetry shell\n```\n\n## `Run`\nTo convert a Huggingface tokenizer to Tensorflow, first choose one from the models or tokenizers from the Huggingface hub to download.\n\n**NOTE**\n> Currently only BERT models work with the converter.\n\n### `Download`\nFirst download tokenizers from the hub by name. Either run the bash script do download multiple tokenizers or download a single tokenizer with the python script.\n\nThe idea is to eventually only to automatically download and convert\n\n```bash\npython tftokenizers/download.py -n bert-base-uncased\nbash scripts/download_tokenizers.sh\n```\n\n### `Convert`\nConvert downloaded tokenizer from Huggingface format to Tensorflow\n```bash\npython tftokenizers/convert.py\n```\n\n## `Before Commit`\n```bash\nmake build\n```\n\n\n\n## WIP\n- [x] Convert a BERT tokenizer from Huggingface to Tensorflow\n- [x] Make a TF Reusabel SavedModel with Tokenizer and Model in the same class. Emulate how the TF Hub example for BERT works.\n- [x] Find methods for identifying the base tokenizer model and map those settings and special tokens to new tokenizers\n- [x] Extend the tokenizers to more tokenizer types and identify them from a huggingface model name\n- [x] Document how others can use the library and document the different stages in the process\n- [x] Improve the conversion pipeline (s.a. Download and export files if not passed in or available locally)\n- [ ] Convert other tokenizers. Identify limitations\n- [ ] Support encoding of two sentences at a time [Ref](https://www.tensorflow.org/text/guide/bert_preprocessing_guide)\n- [ ] Allow the tokenizers to be used for Masking (MLM) [Ref](https://www.tensorflow.org/text/guide/bert_preprocessing_guide)\n',
    'author': 'MarkusSagen',
    'author_email': 'markus.john.sagen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Hugging-Face-Supporter/tftokenizers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
