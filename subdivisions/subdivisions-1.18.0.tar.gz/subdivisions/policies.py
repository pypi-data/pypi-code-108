SQS_IAM = """
{
  "Id": "SQSEventsPolicy",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Allow_SQS_Services",
      "Action": "sqs:*",
      "Effect": "Allow",
      "Resource": "arn:aws:sqs:*",
      "Principal": {
        "AWS": "*"
      }
    }
  ]
}
"""
SNS_IAM = {
    "Version": "2008-10-17",
    "Id": "__default_policy_ID",
    "Statement": [
        {
            "Sid": "__default_statement_ID",
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": [
                "SNS:GetTopicAttributes",
                "SNS:SetTopicAttributes",
                "SNS:AddPermission",
                "SNS:RemovePermission",
                "SNS:DeleteTopic",
                "SNS:Subscribe",
                "SNS:ListSubscriptionsByTopic",
                "SNS:Publish",
                "SNS:Receive",
            ],
            "Resource": "",
        },
        {
            "Sid": "Enable Eventbridge Events",
            "Effect": "Allow",
            "Principal": {"Service": "events.amazonaws.com"},
            "Action": "sns:Publish",
            "Resource": "*",
        },
    ],
}
