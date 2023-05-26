from dagster import DynamicPartitionsDefinition

gameweeks_partitions_def = DynamicPartitionsDefinition(name="gameweeks_partitions_def")
