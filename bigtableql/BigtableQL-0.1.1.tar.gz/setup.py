# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigtableql']

package_data = \
{'': ['*']}

install_requires = \
['datafusion==0.4.0',
 'google-cloud-bigtable==2.4.0',
 'pyarrow==6.0.1',
 'sqloxide==0.1.13']

setup_kwargs = {
    'name': 'bigtableql',
    'version': '0.1.1',
    'description': 'Query Layer for Google Cloud Bigtable',
    'long_description': '# BigtableQL\n\nBigtableQL provides a SQL Query Layer for [Google Cloud Bigtable](https://cloud.google.com/bigtable/docs).\n\n## Use Cases\n\nCloud Bigtable is Google\'s fully managed NoSQL Big Data database service. Each table contains rows and columns. Each row/column intersection can contain multiple cells. Each cell contains a unique timestamped version of the data for that row and column. Thus Bigtable is often used to store time series data.\n\nBigtableQL provides a SQL query layer to run aggregation query on Bigtable.\n\n## Quick Start\n\nUsing the [weather balloon example data](https://cloud.google.com/bigtable/docs/schema-design-time-series#example-data) shown in [Single-timestamp unserialized](https://cloud.google.com/bigtable/docs/schema-design-time-series#unserialized) schema design\n\n```\nRow key                         pressure    temperature humidity    altitude\nus-west2#3698#2021-03-05-1200   94558       9.6         61          612\nus-west2#3698#2021-03-05-1201   94122       9.7         62          611\nus-west2#3698#2021-03-05-1202   95992       9.5         58          602\nus-west2#3698#2021-03-05-1203   96025       9.5         66          598\nus-west2#3698#2021-03-05-1204   96021       9.6         63          624\n```\n\nwe are able to calculate average pressure of the period by\n\n```\nimport bigtableql\n# config follows offical python bigtable client\nclient = bigtableql.Client(config)\n\nclient.register_table(\n    "weather_balloons",\n    instance_id="INSTANCE_ID",\n    column_families={\n        "measurements": {\n            "only_read_latest": True,\n            "columns": {\n                "pressure": int,\n                "temperature": str,\n                "humidity": int,\n                "altitude": int\n            }\n        }\n    }\n)\n\nclient.query("measurements", """\nSELECT avg(pressure) FROM weather_balloons\nWHERE\n  "_row_key" BETWEEN \'us-west2#3698#2021-03-05-1200\' AND \'us-west2#3698#2021-03-05-1204\'\n""")\n```\n\nOr with row key decomposition\n\n```\nclient.register_table(\n    "weather_balloons",\n    instance_id="INSTANCE_ID",\n    column_families={\n        "measurements": {\n            "only_read_latest": True,\n            "columns": {\n                "pressure": int,\n                "temperature": str,\n                "humidity": int,\n                "altitude": int\n            }\n        }\n    },\n    row_key_identifiers=["location", "balloon_id", "event_minute"],\n    row_key_separator="#"\n)\n\nclient.query("measurements", """\nSELECT balloon_id, avg(pressure) FROM weather_balloons\nWHERE\n  location = \'us-west2\'\n  AND balloon_id IN (\'3698\', \'3700\')\n  AND event_minute BETWEEN \'2021-03-05-1200\' AND \'2021-03-05-1204\'\nGROUP BY 1\n""")\n```\n\nThe output of `query` is list of [pyarrow.RecordBatch](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch.from_pydict). It can be easily convert to python dictionary (`to_pydict`) and pandas dataframe (`to_pandas`).\n\n## Alternative\n\n1. [Google BigQuery external data source](https://cloud.google.com/bigquery/external-data-bigtable)\n\nHowever, as of 2022-01, it\n- only supports "us-central1" and "europe-west1" region\n- only supports query with "rowkey"\n- by default can run up to [4 concurrent queries](https://cloud.google.com/bigquery/quotas) against Bigtable external data source\n\n## Roadmap\n\n### SQL\n\n- ✅ Filter (WHERE): "=", "IN", "BETWEEN", ">", ">=", "<", "<="\n- ✅ GROUP BY\n- ✅ ORDER BY\n- ✅ HAVING\n- ✅ LIMIT\n- ✅ Aggregate (e.g. avg, sum, count)\n- ✅ AND\n- [ ] Alias\n- [ ] Cast\n- [ ] Common Math Functions\n- [ ] Common Date/Time Functions\n- [ ] OR ???\n- [ ] Join ???\n- [ ] Insert ???\n\n### General\n\n- ✅ Partition Pruning\n- ✅ Projection pushdown\n- [ ] Predicate push down (only [Value range](https://cloud.google.com/bigtable/docs/using-filters#value-range) is possible)\n- [ ] Limit Pushdown\n\n## Limitation\n\n- for row key encoding, only string is supported\n- for single/composite row key, identifiers supports "=" and "IN". Additionally, last identifier also supports "BETWEEN".\n- for qualifiers, only string and integer (64bit BigEndian encoding) value are supported\n- subqueries and common table expressions are not supported\n\n## Technical Details\n\nBigtableQL depends on\n- [sqloxide](https://github.com/wseaton/sqloxide) and [sqlparser-rs](https://github.com/sqlparser-rs/sqlparser-rs): SQL parser\n- [python-bigtable](https://github.com/googleapis/python-bigtable): offical python bigtable client\n- [datafusion-python](https://github.com/datafusion-contrib/datafusion-python): in memory query engine\n- [pyarrow](https://github.com/apache/arrow/tree/master/python): in memory columnar store / dataframe\n',
    'author': 'jychen7',
    'author_email': 'jychen7@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jychen7/BigtableQL',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
