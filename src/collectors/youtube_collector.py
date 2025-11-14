import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self, api_key, channel_usernames):
        self.api_key = api_key
        self.channel_usernames = channel_usernames
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def _get_video_ids_from_channels(self):
        video_ids = []
        try:
            # Busca os canais pelos usernames para obter seus IDs
            channels_response = self.youtube.channels().list(
                part='contentDetails',
                forUsername=','.join(self.channel_usernames)
            ).execute()

            for channel in channels_response.get('items', []):
                uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
                
                playlist_items_request = self.youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='contentDetails',
                    maxResults=50  # Pega os 50 vídeos mais recentes
                )
                
                while playlist_items_request:
                    playlist_items_response = playlist_items_request.execute()
                    for item in playlist_items_response.get('items', []):
                        video_ids.append(item['contentDetails']['videoId'])
                    
                    playlist_items_request = self.youtube.playlistItems().list_next(
                        playlist_items_request, playlist_items_response
                    )
            
            logger.info(f"Encontrou {len(video_ids)} IDs de vídeo para os canais especificados.")
            return video_ids

        except HttpError as e:
            logger.error(f"Erro na API do YouTube ao buscar vídeos: {e}")
            return []

    def get_all_comments(self):
        logger.info("Iniciando coleta de comentários do YouTube.")
        video_ids = self._get_video_ids_from_channels()
        all_comments = []

        if not video_ids:
            logger.warning("Nenhum ID de vídeo encontrado. Encerrando coleta do YouTube.")
            return []

        for video_id in video_ids:
            try:
                comments_request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100
                )

                while comments_request:
                    comments_response = comments_request.execute()
                    for item in comments_response.get('items', []):
                        comment = item['snippet']['topLevelComment']['snippet']
                        all_comments.append({
                            "id": item['id'],
                            "type": "comment",
                            "text": comment['textOriginal'],
                            "author": comment['authorDisplayName'],
                            "timestamp": comment['publishedAt'],
                            "metadata": {
                                "like_count": comment['likeCount'],
                                "reply_count": item['snippet']['totalReplyCount'],
                                "video_id": comment['videoId']
                            }
                        })
                    
                    if 'nextPageToken' in comments_response:
                        comments_request = self.youtube.commentThreads().list_next(
                            comments_request, comments_response
                        )
                    else:
                        break
                logger.info(f"Coletou comentários do vídeo {video_id}")
            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    logger.warning(f"Comentários desativados para o vídeo {video_id}. Pulando.")
                else:
                    logger.error(f"Erro na API do YouTube para o vídeo {video_id}: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao processar o vídeo {video_id}: {e}")
        
        logger.info(f"Coleta do YouTube finalizada. Total de {len(all_comments)} comentários encontrados.")
        return all_comments