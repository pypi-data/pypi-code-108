from cytoolz.curried import curry

from gosdk import logger


@curry
def process_transcript_batch(data, sdk=None):
    record = {
        "batch": [
            "%s|%s|%s" % (record["chromosome"], record["start"], record["end"])
            for record in data
        ]
    }
    logger.get_logger().debug("get_transcripts_batch", **record)

    results = sdk.call_with_retry(
        sdk.region_search.region_search_batch, **record
    )["results"]

    return results
