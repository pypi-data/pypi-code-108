"""
 The following code snippet shows how to use pyWiliot for Wiliot's cloud services:
 Please change the owner IDs and tag IDs to match your credentials before running the following code
"""

# Import the library
from wiliot.cloud_apis.management.management import *
import os

# Initialise an Wiliot client object
wiliot = ManagementClient(os.environ.get('WILIOT_OAUTH_USERNAME'),
                          os.environ.get('WILIOT_OAUTH_PASSWORD'),
                'test_owner1')

# Define an owner ID
owner_id = "test_owner1"  # ToDo: add here your owner ID

# Get a list of tags owned by the owner
print(wiliot.get_tags())

# Get a list of applications owned by the owner
print(wiliot.get_applications())

# Get tag_1's  details
print(wiliot.get_tag_details("tag_1"))  # ToDo: add here your tag ID and same as for the rest of the code

# Get a list of applications tag_1 is associated with
print(wiliot.get_associated_apps_to_tag("tag_1"))

# Associate tags: tag_1 and tag_2 with the applications: app_1 and app_2
wiliot.associate_tags(["tag_1", "tag_2"], ["app_1", "app_2"])

# Batch associate tags with applications using a CSV file
# The file should have the following format
# tags_file.csv:
#
# tagId,applicationId
# tag_1,app_1
# tag_1,app_2
# tag_2,app_2
# .....
wiliot.batch_associate_tags("/path/to/tags.csv")

# Disassociate tags: tag_1 and tag_2 from applications app_1 and app_2
wiliot.disassociate_tags(["tag_1", "tag_2"], ["app_1", "app_2"])

# Batch disassociate tags using a CSV file. The file format is the
# same as the format CSV file for batch association
wiliot.batch_disassociate_tags("/path/to/tags.csv")

# Create a label
wiliot.create_label("label_1")

# Add tags to the label
wiliot.add_tags_to_label("label_1", ["tag_1", "tag_2"])

# Remove tags from label
wiliot.remove_tags_from_label("label_1", ["tag_1"])

# Associate a label to an application
wiliot.associate_labels(["label_1"], ["app_1", "app_2"])

# Get a list of applications a label is associated to
wiliot.get_associated_apps_to_label("label_1")

# Disassociate a label from an application
wiliot.disassociate_labels(["label_1"], ["app_1", "app_2"])

# Create an application
# First - create an event policy
event_policy = EventPolicy(policy_name="my-policy", filters=[EventFilter(Event.HERE, confidence=0.5),
                                                             EventFilter(Event.GONE, confidence=0.5),
                                                             EventFilter(Event.BACK, confidence=0.5)])
# Then create the application
wiliot.create_application(app_id='test-application-id',
                          app_name='test_application',
                          event_fields=['eventValue', 'eventName', 'tagId'],
                          event_document="{\"eventName\":\"{{eventName}}\", "
                                         "\"eventValue\":\"{{eventValue}}\", "
                                         "\"tagId\":\"{{tagId}}\"}",
                          http_endpoint=HttpEndpoint(url='https://example.com', headers={'Authorization': 'Basic'},
                                                     method='POST'),
                          event_policy=event_policy)
