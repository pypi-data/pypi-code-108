import json
import isodate
import pandas as pd
import os
import pkgutil

save_directory = "YouTube_CSV/"

NUMERR_FLAG = -1
STRERR_FLAG = "unknown"

cate_data = pkgutil.get_data(__name__, "US_CATE.json")
US_CATE = json.loads(cate_data.decode("utf-8"))


class JSONDecoder():
    def __init__(self):
        try:
            os.mkdir(save_directory)
        except OSError:
            print("Directory already exists %s" % save_directory)
        else:
            print("Successfully created the directory %s " % save_directory)

    def _filter_video(self, video):
        if video["channel"] == "error" or video["channel"] == ["error"]:
            return False
        return True

    def _get_duration(self, duration):
        dur = isodate.parse_duration(duration)
        return dur.total_seconds()

    def _get_video_category(self, channel, categoryId):
        categories = []
        if "videoCategories" not in channel:
            categories = US_CATE
        else:
            categories = channel["videoCategories"]["items"]
        for cate in categories:
            if cate["id"] == categoryId:
                return cate["snippet"]["title"]
        for cate in US_CATE:
            if cate["id"] == categoryId:
                return cate["snippet"]["title"]

    def _get_caption_list(self, captions):
        caption = []
        if captions == "error" or captions == ["error"]:
            return caption
        for cap in captions:
            caption.append(cap["text"])
        return json.dumps(caption)

    def _quick_reject(self, data, part):
        if data[part] == "error":
            return True
        if part == "video":
            try:
                if data["channel"] is None \
                        or data["video"] is None \
                        or data["video"]["snippet"] is None \
                        or data["video"]["snippet"]["localized"] is None \
                        or data["video"]["snippet"]["channelId"] is None:
                    return True
            except TypeError or KeyError:
                return True
        if part == "channel":
            try:
                if data["channel"] is None \
                        or data["channel"]["snippet"] is None \
                        or data["channel"]["id"] is None:
                    return True
            except TypeError or KeyError:
                return True
        return False

    def _get_video_obj(self, data):
        if self._quick_reject(data, "video"):
            return None
        return {
            # video_info
            "searchKey": data["searchKey"],
            "embedUrl": "https://www.youtube.com/embed/{0}".format(data["video"]["id"]),
            "videoId": ":" + data["video"]["id"],
            "channelId": data["video"]["snippet"]["channelId"],
            "title": data["video"]["snippet"]["localized"]["title"],
            "tags": json.dumps(data["video"]["snippet"]["tags"]) if "tags" in data["video"]["snippet"] else "[]",
            "duration": self._get_duration(data["video"]["contentDetails"]["duration"]),
            "publishedAt": data["video"]["snippet"]["publishedAt"],
            "categoryId": data["video"]["snippet"]["categoryId"],
            "categories": self._get_video_category(data["channel"], data["video"]["snippet"]["categoryId"]),
            "description": data["video"]["snippet"]["localized"]["description"],
            "commentCount": int(data["video"]["statistics"]["commentCount"]) if "commentCount" in data["video"][
                "statistics"] else NUMERR_FLAG,
            "viewCount": int(data["video"]["statistics"]["viewCount"]) if "viewCount" in data["video"][
                "statistics"] else NUMERR_FLAG,
            "likeCount": int(data["video"]["statistics"]["likeCount"]) if "likeCount" in data["video"][
                "statistics"] else NUMERR_FLAG,
            "dislikeCount": int(data["video"]["statistics"]["dislikeCount"]) if "dislikeCount" in data["video"][
                "statistics"] else NUMERR_FLAG,
            "videoUrl": "https://www.youtube.com/watch?v={0}".format(data["video"]["id"]),
            #             "caption": get_caption_list(data["caption"]),
            "country": data["channel"]["snippet"]["country"] if "country" in data["channel"]["snippet"]
            else STRERR_FLAG,
            "defaultAudioLanguage": data["video"]["snippet"]["defaultAudioLanguage"] if "defaultAudioLanguage" in
                                                                                        data["video"]["snippet"]
            else STRERR_FLAG,
        }

    def _get_category(self, channel):
        result = []
        if "topicDetails" in channel and "topicCategories" in channel["topicDetails"]:
            cate_list = channel["topicDetails"]["topicCategories"]
            for cate in cate_list:
                result.append(cate.split('/')[-1])
        return result

    def _get_channel_obj(self, data):
        if self._quick_reject(data, "channel"):
            return None
        return {
            "channelId": data["channel"]["id"],
            "title": data["channel"]["snippet"]["localized"]["title"],
            "description": data["channel"]["snippet"]["localized"]["description"]
            if "description" in data["channel"]["snippet"]["localized"] else STRERR_FLAG,
            "subscriberCount": int(data["channel"]["statistics"]["subscriberCount"])
            if "subscriberCount" in data["channel"]["statistics"] else NUMERR_FLAG,
            "publishedAt": data["channel"]["snippet"]["publishedAt"]
            if "publishedAt" in data["channel"]["snippet"] else STRERR_FLAG,
            "country": data["channel"]["snippet"]["country"]
            if "country" in data["channel"]["snippet"] else STRERR_FLAG,
            "videoCount": int(data["channel"]["statistics"]["videoCount"]),
            "KEYWORDVideoCount": 1,
            "viewCount": int(data["channel"]["statistics"]["viewCount"]),
            "topicCategories": self._get_category(data["channel"]),
        }

    def _get_comment_obj(self, data):
        if data["comments"] and data["comments"] != "error":
            comments = []
            for c in data["comments"]:
                if "channel" not in data or "video" not in data \
                        or "id" not in data["channel"] or "id" not in data["video"]:
                    continue
                else:

                    comments.append({
                        "embedUrl": "https://www.youtube.com/embed/{0}".format(data["video"]["id"]),
                        "commentId": c["snippet"]["topLevelComment"]["id"] if "topLevelComment" in c[
                            "snippet"] else STRERR_FLAG,
                        "channelId": data["channel"]["id"],
                        "videoId": ":" + data["video"]["id"],
                        "authorDisplayName": c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                        "authorChannelId": c["snippet"]["topLevelComment"]["snippet"]["authorChannelId"][
                            "value"] if "authorChannelId" in c["snippet"]["topLevelComment"][
                            "snippet"] else NUMERR_FLAG,
                        "likeCount": c["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                        "publishedAt": c["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                        "totalReplyCount": c["snippet"]["totalReplyCount"],
                        "textDisplay": c["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                    })
            return comments
        else:
            return None

    def _save_to_csv(self, dlist, name):
        df = pd.DataFrame(data=dlist)
        df.to_csv(name, index=False)

    def json_to_csv(self, data_file):

        if not os.path.exists(save_directory):
            os.mkdir(save_directory)

        video_list = []
        channel_dict = {}
        comment_list = []

        with open(data_file, "r") as fp:
            line = fp.readline()

            while line:
                dataobj = json.loads(line)
                if self._filter_video(dataobj):
                    # get video information
                    video = self._get_video_obj(dataobj)
                    if video:
                        video_list.append(video)

                    # get channel information
                    channel = self._get_channel_obj(dataobj)
                    if channel:
                        channelId = channel["channelId"]
                        if channelId not in channel_dict:
                            channel_dict[channelId] = channel
                        else:
                            channel_dict[channelId]["KEYWORDVideoCount"] += 1

                    # get comment information
                    comments = self._get_comment_obj(dataobj)
                    if comments:
                        comment_list.extend(comments)
                line = fp.readline()

        self._save_to_csv(video_list, f"{save_directory}/videos.csv")
        self._save_to_csv(channel_dict.values(), f"{save_directory}/channels.csv")
        self._save_to_csv(comment_list, f"{save_directory}/comments.csv")
        print(f"Saved files to {save_directory}")
