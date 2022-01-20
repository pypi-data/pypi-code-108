from asyncio import create_task
import json
import time
import httpx
import schedule
import pydash


class LokiTransport:
    def __init__(self, loki_options):
        self.url = loki_options["url"] + "/loki/api/v1/push"
        self.base_labels = loki_options["labels"]
        self.headers = {"Content-type": "application/json"}
        self.streams = []
        self.client = httpx.AsyncClient()
        self.job = schedule.every(5).seconds.do(self.send_batch)

    def prepare_json_streams(self, streams):
        json_streams = []
        for stream in streams:
            values = []
            for entry in stream["entries"]:
                values.append([json.dumps(entry["ts_ns"]), entry["line"]])
            json_streams.append({"stream": stream["labels"], "values": values})
        return json_streams

    def prepare_proto_streams(self, streams):
        proto_streams = []
        for stream in streams:
            labels = pydash.clone_deep(stream["labels"])
            proto_labels = "{"
            proto_labels += f'level="{labels["level"]}"'
            del labels["level"]
            for key in labels:
                proto_labels += f',{key}="{labels[key]}"'
            proto_labels += "}"
            proto_streams.append(
                {
                    "labels": proto_labels,
                    "entries": pydash.map_(
                        stream["entries"],
                        lambda entry: {
                            "line": entry["line"],
                            "ts": json.dumps(entry["ts_ns"] / 1000 / 1000),
                        },
                    ),
                }
            )
        return proto_streams

    async def post(self, payload):
        try:
            async with self.client as client:
                await client.post(self.url, data=payload, headers=self.headers)
        except:
            pass

    def send_batch(self):
        if len(self.streams) == 0:
            return
        json_streams = self.prepare_json_streams(self.streams)
        payload = json.dumps({"streams": json_streams})
        self.streams = []
        create_task(self.post(payload))

    def collect(self, labels, entry):
        for stream in self.streams:
            if pydash.is_equal(stream["labels"], labels):
                stream["entries"].append(entry)
                return
        new_stream = {"labels": labels, "entries": [entry]}
        self.streams.append(new_stream)

    def entry_from_record(self, record):
        return {"ts_ns": time.time_ns(), "line": record["message"]}

    def write(self, record):
        record = record.record
        level = record["level"].name.lower()
        if level == "warning":
            level = "warn"
        labels = {**self.base_labels, "level": level}

        entry = self.entry_from_record(record)
        self.collect(labels, entry)
        if level == "critical":
            self.send_batch()
