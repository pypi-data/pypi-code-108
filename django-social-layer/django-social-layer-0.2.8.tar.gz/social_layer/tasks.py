

from social_layer.mediautils.tasks import formata_all_media
from social_layer.profiles.models import SocialProfilePhoto
from social_layer.posts.models import PostMedia

def format_medias():
    formata_all_media(SocialProfilePhoto)
    formata_all_media(PostMedia)
    
