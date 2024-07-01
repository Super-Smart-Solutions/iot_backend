# from influxdb_client import InfluxDBClient
# from influxdb_client.domain import (
#     GreaterThreshold,
#     LesserThreshold,
#     RangeThreshold,
#     ThresholdCheck,
# )
# from influxdb_client.domain.check_status_level import CheckStatusLevel
# from influxdb_client.domain.dashboard_query import DashboardQuery
# from influxdb_client.domain.query_edit_mode import QueryEditMode
# from influxdb_client.domain.task_status_type import TaskStatusType
# from influxdb_client.service.checks_service import ChecksService

# from iot_backend.settings import settings


# class InfluxDBManger:
#     """
#     A class that manages interactions with InfluxDB, including building checks and queries.

#     This class encapsulates functionalities for interacting with InfluxDB. It allows
#     creating thresholds (checks) based on specific criteria and building queries to
#     retrieve data from the database.

#     Attributes:
#         org_name (str): The name of the organization in InfluxDB.
#         client (InfluxDBClient): An InfluxDBClient instance used for communication.
#         org (Organization): The organization object retrieved from InfluxDB.
#         checks_service (ChecksService): A cached ChecksService instance.
#         bucket (str): The name of the InfluxDB bucket to access (from settings).
#     """
#     def __init__(self):
#         self.bucket = settings.InfluxDB_BUCKET
#         self.org_name = settings.InfluxDB_ORG
#         self.client = InfluxDBClient(
#             url=settings.InfluxDB_URL,
#             token=settings.InfluxDB_TOKEN,
#             org=self.org_name,
#         )
#         self.org = self.client.organizations_api().find_organizations(
#             org=self.org_name
#         )[0]
#         self.checks_service: ChecksService = ChecksService(self.client.api_client)

#     @staticmethod
#     def map_comparator_to_threshold_class(comparator):
#         """
#         Maps a comparator string to the corresponding threshold class.

#         This function takes a comparator string (e.g., "Greater than") and returns
#         the appropriate threshold class from the influxdb_client library.

#         Args:
#             comparator (str): The comparator string (e.g., "Greater than", "Less than", "Range").

#         Returns:
#             The corresponding threshold class (e.g., GreaterThreshold, LesserThreshold, RangeThreshold).
#         """
#         return {
#             "Greater than": GreaterThreshold,
#             "Less than": LesserThreshold,
#             "Range": RangeThreshold,
#         }.get(comparator)

#     def build_threshold(
#         self, name: str, comparator: str, query: str, threshold: float
#     ) -> ThresholdCheck:
#         """
#         Builds and creates a threshold (check) in InfluxDB.

#         This method creates a ThresholdCheck object based on the provided parameters and
#         uses the cached ChecksService to create the check in InfluxDB.

#         Args:
#             name (str): The name of the threshold (check).
#             comparator (str): The comparison operator (e.g., "Greater than", "Less than", "Range").
#             query (str): The InfluxDB query to define the data to monitor.
#             threshold (float): The threshold value for the check.

#         Returns:
#             The response object from the InfluxDB API call for creating the check.
#         """
#         # Find Organization ID by Organization API.
#         threshold_type = self.map_comparator_to_threshold_class(comparator)
#         threshold = threshold_type(value=threshold, level=CheckStatusLevel.CRIT)

#         # Create ThresholdCheck
#         threshold_check = ThresholdCheck(
#             name=name,
#             status_message_template="The value is on: ${ r._level } level!",
#             every="10s",
#             offset="0s",
#             query=DashboardQuery(edit_mode=QueryEditMode.ADVANCED, text=query),
#             thresholds=[threshold],
#             org_id=self.org.id,
#             status=TaskStatusType.ACTIVE,
#         )
#         return self.checks_service.create_check(threshold_check)

#     def disable_check(self, check_id: str):
#         """
#         Disables a check (threshold) in InfluxDB.

#         This method uses the ChecksService to update the status of the specified check to inactive.

#         Args:
#             check_id (str): The ID of the check to disable.

#         Returns:
#             The response object from the InfluxDB API call for updating the check status.
#         """
#         return self.checks_service.patch_checks_id(
#             check_id=check_id, check_patch={"status": TaskStatusType.INACTIVE}
#         )

#     def enable_check(self, check_id: str):
#         """
#         Enables a check (threshold) in InfluxDB.

#         This method uses the ChecksService to update the status of the specified check to active.

#         Args:
#             check_id (str): The ID of the check to enable.

#         Returns:
#             The response object from the InfluxDB API call for updating the check status.
#         """
#         return self.checks_service.patch_checks_id(
#             check_id=check_id, check_patch={"status": TaskStatusType.ACTIVE}
#         )

#     def delete_check(self, check_id: str):
#         """
#         Deletes a check (threshold) from InfluxDB.

#         This method uses the ChecksService to permanently remove the specified check.

#         Args:
#             check_id (str): The ID of the check to delete.

#         Returns:
#             The response object from the InfluxDB API call for deleting the check.
#         """
#         return self.checks_service.delete_checks_id(check_id=check_id)
#     def build_query(self, node_id, channel_id) -> str:
#         """
#         Builds an InfluxDB Flux query to retrieve data.

#         This method constructs a query that filters and aggregates data from a specific InfluxDB bucket
#         based on the provided node and channel IDs.

#         Args:
#             node_id (str): The ID of the node to filter data for.
#             channel_id (str): The ID of the channel to filter data for.

#         Returns:
#             The InfluxDB Flux query string.
#         """
#         return f"""
#         from(bucket: "{self.bucket}")
#             |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
#             |> filter(fn: (r) => r["_measurement"] == "messages")
#             |> filter(fn: (r) => r["publisher"] == "{node_id}")
#             |> filter(fn: (r) => r["channel"] == "{channel_id}")
#             |> filter(fn: (r) => r["_field"] == "value")
#             |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
#             """
