from dagster import resource, StringSource


# Resource to pass google cloud credentials to assets and io_manager
@resource(
    config_schema={
        "project_bucket": StringSource,
        "project_dataset": StringSource,
        "project_ID": StringSource,
    }
)
def google_cloud_config(init_context):
    return {
        "bucket": init_context.resource_config["project_bucket"],
        "dataset": init_context.resource_config["project_dataset"],
        "project_ID": init_context.resource_config["project_ID"],
    }
