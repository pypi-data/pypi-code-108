import boto3

REG_FORM_QUEUE_NAME = "md410-conv-reg-form.fifo"
REG_FORM_QUEUE_URL = (
    "https://sqs.af-south-1.amazonaws.com/960171457841/md410-conv-reg-form.fifo"
)

SESSION = boto3.Session(profile_name="md410-conv")
SQS = SESSION.resource(
    "sqs",
    region_name="af-south-1",
)
REG_FORM_QUEUE = SQS.Queue(REG_FORM_QUEUE_URL)


def send_reg_form_data(data: str):
    response = REG_FORM_QUEUE.send_message(
        MessageBody=data,
        MessageGroupId="reg_form",
    )


def read_reg_form_data(max_number_of_messages=1, timeout=5):
    results = REG_FORM_QUEUE.receive_messages(
        AttributeNames=["All"],
        MaxNumberOfMessages=max_number_of_messages,
        WaitTimeSeconds=timeout,
    )
    [r.delete() for r in results]
    return [r.body for r in results]
