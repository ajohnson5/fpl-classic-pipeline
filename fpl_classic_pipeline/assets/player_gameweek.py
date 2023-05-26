from dagster import asset
import pandas as pd
from fpl_classic_pipeline.utils import gw_stats_api, player_api, team_api
from fpl_classic_pipeline.partitions import gameweeks_partitions_def


@asset(
    partitions_def=gameweeks_partitions_def,
    io_manager_key="gcs_io_manager",
    group_name="Extract_Transform",
)
def player_gameweek(context) -> pd.DataFrame:
    """
    Extracts player data for all players in the Premier League using the FPL
    API endpoints. Asset partitioned by gameweek.

    Args:
        context (OpExecutionContext): object provides system information
        such as resources, config and partitions

    Returns:
        pd.DataFrame: DataFrame containing all players in the Premier League with
        the team they play for and stats for the gameweek(partition).
    """

    # Extract player names and team names and then join.
    player_df = pd.DataFrame(player_api())
    team_df = pd.DataFrame(team_api())
    player_df = player_df.merge(team_df, how="left", on="team_id")

    # Extract stats for all players
    gameweek_stats_df = pd.DataFrame(gw_stats_api(context.partition_key))
    # Convert some stats columns to floats (FPL API stores them as strings)
    cols_to_convert_int = [
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "expected_goals",
        "expected_assists",
        "expected_goal_involvements",
        "expected_goals_conceded",
    ]
    gameweek_stats_df[cols_to_convert_int] = gameweek_stats_df[
        cols_to_convert_int
    ].apply(pd.to_numeric)

    # Join player and stats dataframes
    player_gameweek_df = gameweek_stats_df.merge(player_df, how="left", on="id")
    return player_gameweek_df
