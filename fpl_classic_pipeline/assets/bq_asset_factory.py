from dagster import asset
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from fpl_classic_pipeline.resources import SEASON


bq_asset_defs = [
    {
        "name": "bq_manager_gameweek",
        "non_argument_deps": ["manager_gameweek"],
        "group_name": "Load",
    },
    {
        "name": "bq_manager_gameweek_performance",
        "non_argument_deps": ["manager_gameweek_performance"],
        "group_name": "Load",
    },
    {
        "name": "bq_player_gameweek",
        "non_argument_deps": ["player_gameweek"],
        "group_name": "Load",
    },
]


def bq_asset_factory(bq_asset_config: dict):
    @asset(
        name=bq_asset_config["name"],
        non_argument_deps=bq_asset_config["non_argument_deps"],
        group_name=bq_asset_config["group_name"],
        required_resource_keys={"bq_res", "google_config"},
    )
    def asset_(context) -> None:
        """
        Loads all parquet files created from upstream asset into BigQuery in a
        single table. Note the upstream asset is defined using a
        non-argument dependency.

        Args:
            context (OpExecutionContext): object provides system information
            such as resources, config and partitions

        Returns:
            None:
        """

        gc_config = context.resources.google_config

        # Define job config for BQ, note we overwrite the existing table
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition="WRITE_TRUNCATE",
        )
        # uri to batch load all of the parquet files in the gw_summary directory
        batch_uri = (
            f'gs://{gc_config["bucket"]}/{SEASON}/'
            f'{bq_asset_config["non_argument_deps"][0]}/*.parquet'
        )
        table_name = (
            f'{gc_config["project_ID"]}.{gc_config["dataset"]}.'
            f'{SEASON}_{bq_asset_config["non_argument_deps"][0]}'
        )
        context.resources.bq_res.load_table_from_uri(
            batch_uri,
            table_name,
            job_config=job_config,
        )

        return None

    return asset_
