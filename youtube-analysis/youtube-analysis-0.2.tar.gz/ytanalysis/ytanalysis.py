from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class YTAnalysis:
    
    def __init__(self, channelURL, apikey):
        self.channel_id = channelURL.partition('channel/')[2]
        self.apiKey = apikey
        self.youtube = build('youtube', 'v3', developerKey=self.apiKey)
        self.channel = self.youtube.channels().list(part='snippet,contentDetails,statistics', id = self.channel_id).execute()
        self.channelName = self.channel['items'][0]['snippet']['title']


    def getChannelDetail(self):
        data_dict = dict(
            Name = self.channel['items'][0]['snippet']['title'],
            Subscribers = self.channel['items'][0]['statistics']['subscriberCount'] if self.channel['items'][0]['statistics']['hiddenSubscriberCount'] == False else "null",
            TotalViews = self.channel['items'][0]['statistics']['viewCount'],
            TotalVideos = self.channel['items'][0]['statistics']['videoCount'],
            PlaylistId = self.channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            )

        return data_dict

    def getVideoIds(self):
        playlistId = self.channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        playlist = self.youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlistId,
                maxResults = 50).execute()
        
        self.videoIds = []
        
        for i in range(len(playlist['items'])):
            self.videoIds.append(playlist['items'][i]['contentDetails']['videoId'])
        
        next_page_token = playlist.get('nextPageToken')
        more_pages = True
        
        while more_pages:
            if next_page_token is None:
                more_pages = False
            else:
                playlist = self.youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlistId,
                        maxResults = 50,
                        pageToken = next_page_token).execute()
    
                for i in range(len(playlist['items'])):
                    self.videoIds.append(playlist['items'][i]['contentDetails']['videoId'])
            
                next_page_token = playlist.get('nextPageToken')

        return self.videoIds

    def getVideoDetail(self):
        videoDetails = []
        
        videoIds = self.getVideoIds()
        
        for i in range(0, len(videoIds), 50):
            videoIdReq = self.youtube.videos().list(
                part = 'snippet, statistics',
                id = ','.join(videoIds[i:i+50])
                ).execute()

            for vid in videoIdReq['items']:
                vid_stat = dict(
                    Title = vid['snippet']['title'],
                    Published_date = vid['snippet']['publishedAt'],
                    Views = vid['statistics']['viewCount'],
                    Likes = vid['statistics']['likeCount'],
                    Comments = vid['statistics']['commentCount'])
                videoDetails.append(vid_stat)
    
        return videoDetails

    def export_csv(self):
        data = self.getVideoDetail()
        dataFrame = pd.DataFrame(data)
        dataFrame['Published_date'] = pd.to_datetime(dataFrame['Published_date']).dt.date
        dataFrame['Views'] = pd.to_numeric(dataFrame['Views'])
        dataFrame['Likes'] = pd.to_numeric(dataFrame['Likes'])
        dataFrame.to_csv(f'{self.channelName}_stats.csv')
        
        return None

    def plotViews(self, values=10, mostViewed = True, save=False):
        self.values = values
        data = self.getVideoDetail()
        dataFrame = pd.DataFrame(data)
        dataFrame['Published_date'] = pd.to_datetime(dataFrame['Published_date']).dt.date
        dataFrame['Views'] = pd.to_numeric(dataFrame['Views'])
        dataFrame['Likes'] = pd.to_numeric(dataFrame['Likes'])
        
        if mostViewed:
            order = False
        else:
            order = True

        top_videos = dataFrame.sort_values(by='Views', ascending=order).head(self.values)

        bar = sns.barplot(data = top_videos, x='Views', y='Title')
        
        if save==True:
            bar.get_figure().savefig(f'{self.channelName} most viewed.png')
        else: 
            pass
        
        return plt.show()


    def plotVideoCount(self, save=False):
        data = self.getVideoDetail()
        dataFrame = pd.DataFrame(data)
        dataFrame['Published_date'] = pd.to_datetime(dataFrame['Published_date']).dt.strftime('%b')
        dataFrame = dataFrame.groupby('Month', as_index=False).size()
        sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        dataFrame.index = pd.CategoricalIndex(dataFrame['Month'], categories=sort_order, ordered=True) 
        dataFrame = dataFrame.sort_index()

        bar = sns.barplot(x='Month', y='Frequency', data=dataFrame)

        if save==True:
            bar.get_figure().savefig(f'{self.channelName} video posted per month.png')
        else: 
            pass
        
        return plt.show()
