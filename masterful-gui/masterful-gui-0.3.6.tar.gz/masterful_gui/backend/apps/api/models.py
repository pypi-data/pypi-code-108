from django.db import models


class PolicySearchTask(models.Model):
  """The main PolicySearchTask model.
  
  The model mirrors the PolicySearchTask proto. Scalar fields are assigned
  similaer fields in the model, everything else is assigned JSON fields.
  """
  # The name of the policy. This is the primary key of the model.
  policy_name = models.CharField(primary_key=True, max_length=250)

  # The name of the approach.
  approach_name = models.CharField(max_length=120)

  # Node search tasks performed in the policy search task.
  node_search_tasks = models.JSONField(default=dict)

  # Metrics specific to the customer model without any Masterful improvements.
  presearch_model_val_metrics = models.JSONField(default=dict)

  # The version of the policy engine that produced this policy.
  engine_version = models.CharField(default="", max_length=100)


class DatasetSpec(models.Model):
  """A model that holds the metadata of a dataset.
  
  The model mirrors the DatasetSpec proto. For full documentation see the
  proto definition.
  """
  # The title of the dataset. This is the primary key of the model.
  title = models.CharField(primary_key=True, max_length=250)

  # The split of the dataset.
  split = models.CharField(default="SPLIT_UNKNOWN", max_length=50)

  # Cardinality of the dataset regardless of split.
  total_cardinality = models.IntegerField(default=0)

  # Train dataset cardinality if the dataset was the full dataset.
  train_cardinality = models.IntegerField(default=0)

  # Validation dataset cardinality if the dataset was the full dataset.
  val_cardinality = models.IntegerField(default=0)

  # Test dataset cardinality if the dataset was the full dataset.
  test_cardinality = models.IntegerField(default=0)

  # Maps label numeric form to text form.
  labels_map = models.JSONField(default=dict)

  # Label distribution in the dataset. This is set regardless of split.
  total_label_distribution = models.JSONField(default=dict)

  # Label distribution in the train dataset.
  train_label_distribution = models.JSONField(default=dict)

  # Label distribution in the validation dataset.
  val_label_distribution = models.JSONField(default=dict)

  # Label distribution in the test dataset.
  test_label_distribution = models.JSONField(default=dict)

  # Image specs of the data.
  image_spec = models.JSONField(default=dict)

  # The computer vision task the dataset is meant for.
  task = models.CharField(default="COMPUTER_VISION_TASK_UNKNOWN",
                          max_length=250)

  # Number of classes (labels) in the dataset.
  num_classes = models.IntegerField(default=0)