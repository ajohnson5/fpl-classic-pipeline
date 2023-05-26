from dagster import asset, OpExecutionContext
from google.cloud import bigquery
from fpl_classic_pipeline.partitions import gameweeks_partitions_def
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
        "table_names": ["2022_manager_gameweek_performance", "2022_manager_gameweek"],
        "group_name": "Analysis",
        "sql": summary_stats,
    },
    {
        "name": "manager_rank",
        "non_argument_deps": ["bq_manager_gameweek_performance"],
        "table_names": "2022_manager_gameweek_performance",
        "group_name": "Analysis",
        "sql": manager_rank,
    },
    {
        "name": "transfers",
        "non_argument_deps": ["bq_manager_gameweek", "bq_player_gameweek"],
        "table_names": ["2022_manager_gameweek", "2022_player_gameweek"],
        "group_name": "Analysis",
        "sql": transfers,
    },
    {
        "name": "points_on_bench",
        "non_argument_deps": ["bq_manager_gameweek", "bq_manager_gameweek_performance"],
        "table_names": ["2022_manager_gameweek", "2022_manager_gameweek_performance"],
        "group_name": "Analysis",
        "sql": points_on_bench,
    },
    {
        "name": "chip_usage",
        "non_argument_deps": ["bq_manager_gameweek_performance"],
        "table_names": "2022_manager_gameweek_performance",
        "group_name": "Analysis",
        "sql": chip_usage,
    },
]


def execute_bigquery(
    context: OpExecutionContext, table_names, sql: str, partition_key: str = ""
) -> pd.DataFrame:
    gc_config = context.resources.google_config
    if isinstance(table_names, list):
        table_path = (
            f'{gc_config["project_ID"]}.{gc_config["dataset"]}.{table_names[0]}'
        )
        sql = sql.replace("$", table_path)
        table_path = (
            f'{gc_config["project_ID"]}.{gc_config["dataset"]}.{table_names[1]}'
        )
        sql = sql.replace("^", table_path)
    else:
        table_path = f'{gc_config["project_ID"]}.{gc_config["dataset"]}.{table_names}'
        sql = sql.replace("$", table_path)

    sql = sql.replace(
        "&", f'{",".join([str(x) for x in range(1,int(context.partition_key)+1)])}'
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "prev_gameweek", "INT64", int(partition_key) - 1
            ),
            bigquery.ScalarQueryParameter("gameweek", "INT64", int(partition_key)),
        ]
    )
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
