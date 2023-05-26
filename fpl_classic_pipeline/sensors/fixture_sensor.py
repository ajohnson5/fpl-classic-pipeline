from dagster import (
    sensor,
    AssetSelection,
    RunRequest,
    SkipReason,
    DefaultSensorStatus,
)
from fpl_classic_pipeline.utils.fpl_getter import gw_completed_api


@sensor(
    asset_selection=AssetSelection.all(),
    minimum_interval_seconds=43200,
    default_status=DefaultSensorStatus.RUNNING,
)
def fixture_sensor(context):
    """
    Sensor checks to see if gameweek has been completed and adds dynamic partition for
    that gameweek and then materializes all assets with that partition key.

    Args:
        context (OpExecutionContext): object provides system information
        such as resources, config and partitions

    Returns:
        SkipRequest: If gameweek is not finished a SkipRequest is returned so assets
        are not materialized
        RunRequest: If gameweek is completed then assets are materialized for newly
        added partition
    """

    partition_key = context.cursor or "1"
    if not gw_completed_api(partition_key):
        return SkipReason("Current gameweek is not completed")

    context.instance.add_dynamic_partitions("gameweeks_partitions_def", [partition_key])
    run_request = RunRequest(
        run_key=partition_key, run_config={}, partition_key=partition_key
    )
    # Increment cursor by one
    context.update_cursor(str(int(partition_key) + 1))
    return run_request
