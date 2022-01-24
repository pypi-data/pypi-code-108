import boto3

class SnsService:
    def send(self, topic_arn, subject, message):
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message,
            MessageAttributes={}
        )
