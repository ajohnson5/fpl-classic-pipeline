import pandas as pd
from dagster import (
    IOManager,
    io_manager,
)

# Define season for GCS directory structure
SEASON = "2022"


class GCSParquetIOManager(IOManager):
    """IO Manager which stores parquet files in GCS and takes data in as a dataframe"""

    def __init__(self, bucket_name: str, prefix="", season="2022"):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.season = season

    def _get_gcs_url(self, context):
        """Creates and returns GCS uri for loading and storing outputs"""
        if context.has_partition_key and context.has_asset_partitions:
            file_name = f"{context.asset_key.path[-1]}_{context.asset_partition_key}"
        else:
            file_name = context.asset_key.path[-1]
        asset_name = context.asset_key.path[-1]
        self.gs_uri = (
            f"gs://{self.bucket_name}/{self.season}/"
            f"{asset_name}/{self.prefix}{file_name}.parquet"
        )
        return self.gs_uri

    def handle_output(self, context, df: pd.DataFrame):
        """Stores pandas DataFrames as Parquet files in GCS"""
        if df is None:
            return

        if not isinstance(df, pd.DataFrame):
            raise ValueError(r"Expected asset to return a pd.DataFrame; got a {df!r} ")

        file_name = self._get_gcs_url(context)

        df.to_parquet(file_name, index=False)

    def load_input(self, context) -> pd.DataFrame:
        """Reads data from GCS uri as pandas DataFrames"""
        df = pd.read_parquet(self._get_gcs_url(context))

        return df


@io_manager(required_resource_keys={"gcs", "google_config"})
def gcs_parquet_io_manager(init_context):
    return GCSParquetIOManager(
        bucket_name=init_context.resources.google_config["bucket"],
        season=SEASON,
    )
