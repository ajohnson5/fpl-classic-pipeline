from dagster import asset, OpExecutionContext
from google.cloud import bigquery
from fpl_classic_pipeline.partitions import gameweeks_partitions_def
from fpl_classic_pipeline.resources import SEASON
import pandas as pd
from fpl_classic_pipeline.assets.queries import (
    transfers,
    summary_stats,
    manager_rank,
    points_on_bench,
    chip_usage,
)


query_asset_defs = [
    {
        "name": "summary_stats",
        "non_argument_deps": ["bq_manager_gameweek_performance", "bq_manager_gameweek"],
        "table_names": [
            f"{SEASON}_manager_gameweek_performance",
            f"{SEASON}_manager_gameweek",
        ],
        "group_name": "Analysis",
        "sql": summary_stats,
    },
    {
        "name": "manager_rank",
        "non_argument_deps": ["bq_manager_gameweek_performance"],
        "table_names": [f"{SEASON}_manager_gameweek_performance"],
        "group_name": "Analysis",
        "sql": manager_rank,
    },
    {
        "name": "transfers",
        "non_argument_deps": ["bq_manager_gameweek", "bq_player_gameweek"],
        "table_names": [f"{SEASON}_manager_gameweek", f"{SEASON}_player_gameweek"],
        "group_name": "Analysis",
        "sql": transfers,
    },
    {
        "name": "points_on_bench",
        "non_argument_deps": ["bq_manager_gameweek", "bq_manager_gameweek_performance"],
        "table_names": [
            f"{SEASON}_manager_gameweek",
            f"{SEASON}_manager_gameweek_performance",
        ],
        "group_name": "Analysis",
        "sql": points_on_bench,
    },
    {
        "name": "chip_usage",
        "non_argument_deps": ["bq_manager_gameweek_performance"],
        "table_names": [f"{SEASON}_manager_gameweek_performance"],
        "group_name": "Analysis",
        "sql": chip_usage,
    },
]


def execute_bigquery(
    context: OpExecutionContext, table_names, sql: str, partition_key: str = ""
) -> pd.DataFrame:
    """
    Constructs and executes a parametrised SQL query using BigQuery. Note you are
    unable to parametrise table names,thus tables names have been replaced with
    placeholders such as $ and ^ in the SQL queries. These placeholders are replaced
    with the table names before query is executed
    Args:
        context (OpExecutionContext): object provides system information
        such as resources, config and partitions
        table_names: List of table names used in the SQL query
        sql: Parametrised SQL query
        partition_key: Gameweek partition to use in SQL query

    Returns:
        pd.DataFrame: DataFrame containing the results of the sql query

    """
    gc_config = context.resources.google_config
    # Define indicators that will be replaced with BigQuery table names
    sql_replace_placeholder = ["$", "^"]
    # Iterate through tables used in the SQL queries and replace the placeholder with
    # the table names
    for i, table_name in enumerate(table_names):
        table_path = f'{gc_config["project_ID"]}.{gc_config["dataset"]}.{table_name}'
        sql = sql.replace(sql_replace_placeholder[i], table_path)

    # Define BigQuery query config with gameweek parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "prev_gameweek", "INT64", int(partition_key) - 1
            ),
            bigquery.ScalarQueryParameter("gameweek", "INT64", int(partition_key)),
        ]
    )
    # Execute query and return as a dataframe
    query_results = context.resources.bq_res.query(sql, job_config=job_config)
    return query_results.to_dataframe()


def query_asset_factory(dict_: dict):
    @asset(
        name=dict_["name"],
        non_argument_deps=dict_["non_argument_deps"],
        group_name=dict_["group_name"],
        required_resource_keys={"bq_res", "google_config"},
        partitions_def=gameweeks_partitions_def,
        io_manager_key="gcs_io_manager",
    )
    def asset_(context) -> pd.DataFrame:
        return execute_bigquery(
            context=context,
            table_names=dict_["table_names"],
            sql=dict_["sql"],
            partition_key=context.partition_key,
        )

    return asset_
