from dagster import asset
import pandas as pd
import os
from fpl_classic_pipeline.utils import manager_id_from_league_api, manager_gw_picks_api
from fpl_classic_pipeline.partitions import gameweeks_partitions_def

league_id = os.getenv("LEAGUE_ID", "1")


@asset(
    partitions_def=gameweeks_partitions_def,
    io_manager_key="gcs_io_manager",
    group_name="Extract_Transform",
)
def manager_gameweek(context, player_gameweek) -> pd.DataFrame:
    """
    Extracts manager pick data for specified league using FPL API endpoints and joins
    this data with the player gameweek stats. Asset partitioned by gameweek.

    Args:
        context (OpExecutionContext): object provides system information
        such as resources, config and partitions
        player_gameweek (pd.DataFrame): DataFrame containing list of all players and
        their gameweek stats.

    Returns:
        pd.DataFrame: DataFrame containing all of the picks each manager in the
        specified league made during the gameweek and the stats for all of these
        players.
    """
    # Extract list of managers in league
    managers = [x["manager_id"] for x in manager_id_from_league_api(league_id)]

    # Extract each pick each manager made in the league
    manager_picks = []
    for manager in managers:
        manager_picks += manager_gw_picks_api(context.partition_key, manager)
    picks_df = pd.DataFrame(manager_picks)

    manager_gameweek_df = picks_df.merge(player_gameweek, how="left", on="id")

    # Add column which calculates the actual points each player gives a manager (chips)
    # Note that multiplier column factors bench boost and triple captain chips
    manager_gameweek_df["actual_points"] = (
        manager_gameweek_df["total_points"] * manager_gameweek_df["multiplier"]
    )
    return manager_gameweek_df
