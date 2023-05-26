from dagster import Definitions
from dagster_gcp.gcs import gcs_resource
from dagster_gcp import bigquery_resource
from fpl_classic_pipeline.assets import (
    player_gameweek,
    manager_gameweek,
    manager_gameweek_performance,
    query_asset_defs,
    query_asset_factory,
    bq_asset_defs,
    bq_asset_factory,
)
from fpl_classic_pipeline.sensors import fixture_sensor
from fpl_classic_pipeline.resources import google_cloud_config, gcs_parquet_io_manager


# Configure resources for the deployment environments (development/production)
resource_env = {
    "google_config": google_cloud_config.configured(
        {
            "project_bucket": {"env": "PROJECT_BUCKET"},
            "project_dataset": {"env": "PROJECT_DATASET"},
            "project_ID": {"env": "PROJECT_ID"},
        }
    ),
    "gcs_io_manager": gcs_parquet_io_manager,
    "gcs": gcs_resource,
    "bq_res": bigquery_resource,
}


defos = Definitions(
    assets=[
        player_gameweek,
        manager_gameweek,
        manager_gameweek_performance,
    ]
    + [query_asset_factory(x) for x in query_asset_defs]
    + [bq_asset_factory(x) for x in bq_asset_defs],
    resources=resource_env,
    sensors=[fixture_sensor],
)
