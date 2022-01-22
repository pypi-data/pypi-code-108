import time

from google.cloud import bigquery, storage


class BQChartData:
    """
    Highly specialized Interface to BigQuery-based US ETF data

    Preconditions:
        - There is a GCP project with BQ and GCS enabled

        - The environment variable GOOGLE_APPLICATION_CREDENTIALS points to a file granting access to these services

        - There is a BigQuery table in some given dataset with 1-min OHLCV data for some symbols

        - If there's no table yet, you can create one from appropriately structured CSV files
            in a given bucket using load_from_bucket()

        - The BigQuery table used for querying eventually must have the desired schema (the order matters!):
            bigquery.SchemaField("DATE_TIME", "DATETIME"),
            bigquery.SchemaField("OPEN", "FLOAT"),
            bigquery.SchemaField("HIGH", "FLOAT"),
            bigquery.SchemaField("LOW", "FLOAT"),
            bigquery.SchemaField("CLOSE", "FLOAT"),
            bigquery.SchemaField("VOLUME", "INTEGER"),
            bigquery.SchemaField("SYMBOL", "STRING", max_length=16)
    """

    def __init__(self, project_id: str, dataset_name: str, table_name: str, verbose=False):
        self.table_id = f"{project_id}.{dataset_name}.{table_name}"
        self.bq_client = bigquery.Client()
        self.gcs_client = storage.Client()
        if verbose:
            print(f"Using table: {self.table_id}")
        self.schema = [
            bigquery.SchemaField("DATE_TIME", "DATETIME"),
            bigquery.SchemaField("OPEN", "FLOAT"),
            bigquery.SchemaField("HIGH", "FLOAT"),
            bigquery.SchemaField("LOW", "FLOAT"),
            bigquery.SchemaField("CLOSE", "FLOAT"),
            bigquery.SchemaField("VOLUME", "INTEGER"),
            bigquery.SchemaField("SYMBOL", "STRING", max_length=16)
        ]

    def load_from_bucket(self, bucket, batch_size=2, n_batches=None, sleep=10, verbose=False):
        """
        ATTENTION: This will truncate the table if it already exists!

        Load a number of files in batches of given size. Typically processes files alphabetically.
        Assumes the schema as given in the constructor
        """
        files = [blob.name for blob in self.gcs_client.list_blobs(bucket)]
        n_batches = n_batches or len(files) // batch_size
        if verbose:
            symbols = [f.split("/")[1].split("_")[0] for f in files]
            print(f"Uploading for symbols: {symbols[:n_batches * batch_size + 1]}")
            print(f"Starting with symbol {symbols[0]}.")
        self.load_file(bucket, files[0], bigquery.WriteDisposition.WRITE_TRUNCATE)
        for i in range(n_batches):
            # Wait a bit to avoid HTTP403 rate limit violations
            time.sleep(sleep)
            batch = files[i * batch_size + 1:(i + 1) * batch_size + 1]
            symbols = [f.split("/")[1].split("_")[0] for f in batch]
            if verbose:
                print(f"Loading symbols {symbols}.")
            for file in batch:
                self.load_file(bucket, file, bigquery.WriteDisposition.WRITE_APPEND)

            if verbose:
                destination_table = self.bq_client.get_table(self.table_id)
                print(f"Total rows now {destination_table.num_rows}")

    def load_file(self, bucket, file, mode: bigquery.WriteDisposition):
        """
        Upload CSV from a well-defined CSV file in a particular bucket
        """
        job_config = bigquery.LoadJobConfig(
            schema=self.schema,
            write_disposition=mode,
            source_format=bigquery.SourceFormat.CSV
        )

        return self.bq_client.load_table_from_uri(
            f"gs://{bucket}/{file}",
            self.table_id,
            job_config=job_config
        )

    def get_daily_close_and_volume(self, symbol):
        query = f"""
                    SELECT  
                        DATE(DATE_TIME) as `date`,
                        extract(YEAR FROM DATE(DATE_TIME)) as year,
                        extract(MONTH FROM DATE(DATE_TIME)) as month,
                        extract(DAY FROM DATE(DATE_TIME)) as day,
                        extract(DAYOFWEEK FROM DATE(DATE_TIME)) as weekday,
                        ARRAY_AGG(close ORDER BY DATE_TIME DESC)[OFFSET(0)] AS close,
                        sum(VOLUME) as volume
                    FROM `{self.table_id}` 
                    WHERE symbol = '{symbol}'
                    group by symbol, year, month, day, weekday, `date`
                    order by symbol, year, month, day
                """
        return self.bq_client.query(query).result().to_dataframe()
