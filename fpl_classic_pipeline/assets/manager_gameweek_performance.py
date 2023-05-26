from dagster import asset
import pandas as pd
import os
from fpl_classic_pipeline.utils import (
    manager_gw_performance_api,
    manager_id_from_league_api,
)
from fpl_classic_pipeline.partitions import gameweeks_partitions_def

league_id = os.getenv("LEAGUE_ID", "1")


@asset(
    partitions_def=gameweeks_partitions_def,
    io_manager_key="gcs_io_manager",
    group_name="Extract_Transform",
)
def manager_gameweek_performance(context):
    """
    Extracts manager performance data using the FPL API endpoints for all
    managers in the specified league. Asset partitioned by gameweek.

    Args:
        context (OpExecutionContext): object provides system information
        such as resources, config and partitions

    Returns:
        pd.DataFrame: DataFrame containing manager performance data for each gameweek.
    """
    # Using league 1 as an example but will be changed later
    managers = [x["manager_id"] for x in manager_id_from_league_api(league_id)]

    manager_performance = []
    for manager in managers:
        # Iterate through managers adding their performance for each week
        manager_performance += manager_gw_performance_api(
            context.partition_key, manager
        )
    return pd.DataFrame(manager_performance)
