from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from rest_framework.fields import ReadOnlyField
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailmedia.edit_handlers import MediaChooserPanel

from mycarehub.common.models import AbstractBase
from mycarehub.content.serializers import MediaSerializedField

RICH_TEXT_FIELD_FEATURES = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "bold",
    "italic",
    "ol",
    "ul",
    "hr",
    "link",
    "document-link",
    "image",
    "embed",
    "blockquote",
    "superscript",
    "subscript",
    "strikethrough",
]


@register_snippet
class Author(AbstractBase):
    """
    Author holds an author and their avatar (image).

        - the `title` field is used for the author's display name.
        - the `data` field contains the avatar (author's image).
    """

    name = models.CharField(max_length=128, help_text="Author's name (will be displayed publicly)")
    avatar = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="author_image",
        help_text="An optional author picture (will be displayed publicly)",
    )

    panels = [
        FieldPanel("name"),
        ImageChooserPanel("avatar"),
    ]

    def __str__(self):
        """Represent an author by their name."""
        return self.name

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "authors"


@register_snippet
class ContentItemCategory(models.Model):
    """
    ContentItemCategory defines fixed (admin rather than author/editor defined)
    categories for content.

    It should be used to set up "predictable" categories e.g welcome content,
    diet, fitness, onboarding etc.
    """

    name = models.CharField(
        max_length=255,
        help_text="A standard name for a type of content e.g fitness, diet etc. "
        "These will be used in the user interface to group content so they "
        "should be chosen carefully.",
    )
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="content_item_category_icons",
        help_text="An optional icon for the content item category. "
        "This will be shown in the user interface so it should be chosen "
        "with care.",
    )

    panels = [
        FieldPanel("name"),
        ImageChooserPanel("icon"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "content item categories"


class ContentItemTag(TaggedItemBase):
    """
    ContentItemTag is used to associate content items with tags.

    The underlying mechanism is based on django-taggit.
    """

    content_object = ParentalKey(
        "ContentItem",
        related_name="tagged_items",
        on_delete=models.CASCADE,
        help_text="Associated content item",
    )


class ContentItemTagIndexPage(Page):
    """
    This sets up a page that lists content items by tag

    e.g https://<site>/?tag=<tag>
    """

    parent_page_types = [
        "home.HomePage",
    ]

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get("tag")
        content_items = ContentItem.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context["tagged_items"] = content_items
        return context


class ContentItemIndexPage(Page):
    """
    This sets up a page that lists content items in reverse chronological order

    i.e an "articles" or "content" home page
    """

    intro = RichTextField(default=f"{settings.SITE_NAME}", help_text="The content site's tagline")

    content_panels = Page.content_panels + [
        FieldPanel("intro", classname="full"),
    ]
    api_fields = [
        APIField("intro"),
    ]
    parent_page_types = [
        "home.HomePage",
    ]
    subpage_types = [
        "content.ContentItem",
    ]

    def get_context(self, request):
        # Update context to include only published posts
        # ordered in reverse-chronological order (most recent items first)
        context = super().get_context(request)
        content_items = self.get_children().live().order_by("-first_published_at")
        context["content_items"] = content_items
        return context


class ContentItem(Page):
    """
    A `ContentItem` is an article, video, document etc. These are managed using
    the Wagtail CMS.

    - when the item is published, the `live` boolean is flipped to `True`
    (and vice-versa)
    """

    class ItemTypes(models.TextChoices):
        ARTICLE = "ARTICLE"
        AUDIO_VIDEO = "AUDIO_VIDEO"
        PDF_DOCUMENT = "PDF_DOCUMENT"

    # basic properties that each post has
    date = models.DateField(
        "Post date",
        help_text="This will be shown to readers as the publication date",
    )
    intro = models.CharField(
        max_length=250,
        help_text="A teaser that will be shown when it's inappropriate "
        "to show the entire article",
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        help_text="The item's author. This will be displayed on the website and apps.",
    )
    item_type = models.CharField(
        max_length=64,
        choices=ItemTypes.choices,
        help_text="Whether this item is an article, audio/video or document. "
        "This is used by the mobile app to determine how to render content. "
        "e.g with an article, the layout will be hero_image > body while for "
        "audio-visual content the media will come first and the body last. "
        "For documents, the document(s) will also be presented before the "
        "body text.",
    )
    time_estimate_seconds = models.PositiveIntegerField(
        default=0,
        help_text="An estimate of how long it will take to read the article, "
        "in seconds. The mobile app(s) and website will render this in a more "
        "friendly form e.g minutes, hours etc.",
    )

    # this must be set for articles (otherwise the content does not make sense)
    body = RichTextField(
        features=RICH_TEXT_FIELD_FEATURES,
        help_text="The main article text, video description, audio file "
        "description or document description.",
    )

    # content items are classified using tags or categories
    # tags are "free form" i.e editors can add and modify them at will
    # while categories are defined in a database table and picked from a
    # drop-down list
    tags = ClusterTaggableManager(
        through=ContentItemTag,
        help_text="These are labels that you can apply to the content on the "
        "basis of your editorial policy. You need to define at least one tag. "
        "The choice of tag(s) should be guided by your editorial manual i.e "
        "the decisions that have been made about how to label content. ",
    )

    categories = ParentalManyToManyField(
        ContentItemCategory,
        help_text="These are fixed categories (picked from a list set up by "
        "the system administrators) that determine what content is presented "
        "to readers e.g only content in the 'welcome' category will be shown "
        "as welcome content. Each content item must have at least one category.",
    )

    # a post can feature an image OR other media (audio, video) at the top
    # this is optional. When present, it is displayed as a banner before the
    # content item e.g before the text of an article
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        related_name="content_hero_image",
        null=True,
        blank=True,
        help_text="An optional banner image. When present, it will be displayed "
        "above the content e.g above the article. This makes sense mostly for "
        "text articles.",
    )

    # these fields record interactions with the content and are calculated and
    # cached. These fields should be read-only in the CMS and admin. For that
    # reason, they do not have help text.
    like_count = models.PositiveIntegerField(default=0)
    bookmark_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    @property
    def author_name(self):
        return self.author.name

    @property
    def author_avatar_url(self):
        return self.author.avatar.url if self.author.avatar is not None else ""

    @property
    def category_details(self):
        return [
            {
                "category_id": cat.id,
                "category_name": cat.name,
                "category_icon": cat.icon.file.url if cat.icon is not None else "",
            }
            for cat in self.categories.all()
        ]

    @property
    def tag_names(self):
        return [tag.name for tag in self.tags.all()]

    def clean(self):
        if self.item_type == "ARTICLE" and self.hero_image is None:
            raise ValidationError("an article must have a hero image")

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("tags"),
                FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
            ],
            heading="About",
        ),
        FieldPanel("author"),
        FieldPanel("item_type"),
        FieldPanel("intro"),
        ImageChooserPanel("hero_image"),
        FieldPanel("body", classname="full"),
        FieldPanel("time_estimate_seconds"),
        # documents, images and media attached to content item pages
        # a content item can have zero or more of each of these
        InlinePanel("gallery_images", label="Gallery images"),
        InlinePanel("documents", label="Documents"),
        InlinePanel("featured_media", label="Audio and Video (media)"),
    ]

    # these fields determine the content that is indexed for search purposes
    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    # this configuration allows these custom fields to be available over the API
    api_fields = [
        APIField("date"),
        APIField("intro"),
        APIField("author"),
        APIField("author_name"),
        APIField("author_avatar_url"),
        APIField("item_type"),
        APIField("time_estimate_seconds"),
        APIField("body"),
        APIField("tag_names"),
        APIField("hero_image"),
        APIField(
            "hero_image_rendition",
            serializer=ImageRenditionField(
                "fill-800x1200|jpegquality-60",
                source="hero_image",
            ),
        ),
        APIField("like_count"),
        APIField("bookmark_count"),
        APIField("view_count"),
        APIField("share_count"),
        APIField("documents"),
        APIField(
            "featured_media",
            serializer=MediaSerializedField(),
        ),
        APIField("gallery_images"),
        APIField("questionnaires"),
        APIField(
            "category_details",
            serializer=ReadOnlyField(),
        ),
    ]

    # limit the parent page types
    parent_page_type = [
        "content.ContentItemIndexPage",
    ]


class ContentItemDocumentLink(Orderable):
    """
    A content item can have multiple documents attached to it.

    This is configured through this model.
    """

    page = ParentalKey(ContentItem, related_name="documents")
    document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.CASCADE,
        related_name="content_item_documents",
        help_text="Select or upload a PDF document. It is IMPORTANT to limit "
        "these documents to PDFs - otherwise the mobile app may not be able "
        "to display them properly.",
    )

    panels = [
        DocumentChooserPanel("document"),
    ]
    api_fields = [
        APIField("document"),
    ]

    class Meta:
        unique_together = (
            "page",
            "document",
        )


class ContentItemMediaLink(Orderable):
    """
    A content item can have multiple audio and video files attached to it.

    This is configured through this model.
    """

    page = ParentalKey(
        ContentItem,
        related_name="featured_media",
    )
    featured_media = models.ForeignKey(
        "wagtailmedia.Media",
        on_delete=models.CASCADE,
        related_name="content_item_media",
        help_text="Select or upload an audio or video file. "
        "In order to maximize compatibility, please stick to common audio/video "
        "formats. For video, H264 encoded MP4 files are recommended. "
        "For audio, AAC (Advanced Audio Codec) files are recommended. ",
    )

    panels = [
        MediaChooserPanel("featured_media"),
    ]
    api_fields = [
        APIField("featured_media"),
    ]

    class Meta:
        unique_together = (
            "page",
            "featured_media",
        )


class ContentItemGalleryImage(Orderable):
    page = ParentalKey(ContentItem, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="content_item_gallery_images",
        help_text="Select or upload an image. Most of these images will be viewed on mobile "
        "devices. The ideal image should be large enough to render clearly on high end mobile "
        "devices but not so large that it costs a lot of bandwidth to download. One good size "
        "guideline to aim for is 800x1200 pixels. This is a guideline, not an iron-clad rule.",
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel("image"),
        FieldPanel("caption"),
    ]
    api_fields = [
        APIField("image"),
    ]


class ContentInteraction(AbstractBase):
    """
    This is an abstract base model that is used to hold common fields and
    behaviours for content interactions e.g like, save, share etc.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    content_item = models.ForeignKey(ContentItem, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class ContentLike(ContentInteraction):
    """
    When a user likes a content item, an entry is added here and the cached
    count on the content item is updated.

    When a user unlikes a content item, the entry here is removed and the cached
    count on the content item is updated.

    These updates should be performed in a transaction - with special care
    taken to ensure that the incremeting and decrementing of the cached counts
    is not prone to race conditions.
    """

    class Meta:
        unique_together = (
            "user",
            "content_item",
        )


class ContentBookmark(ContentInteraction):
    """
    When a user bookmarks (saves or pins) a content item, an entry is added
    here and the cached count on the content item is updated.

    When a user removes a bookmark, the entry here is removed and the cached
    count on the content item is updated.

    These updates should be performed in a transaction - with special care
    taken to ensure that the incremeting and decrementing of the cached counts
    is not prone to race conditions.
    """

    class Meta:
        unique_together = (
            "user",
            "content_item",
        )


class ContentShare(ContentInteraction):
    """
    When a user shares a content item, an entry is added
    here and the cached count on the content item is updated.

    There is no notion of "unsharing".

    These updates should be performed in a transaction - with special care
    taken to ensure that the incremeting and decrementing of the cached counts
    is not prone to race conditions.
    """

    class Meta:
        unique_together = (
            "user",
            "content_item",
        )


class ContentView(ContentInteraction):
    """
    When a user views a content item, an entry is added
    here and the cached count on the content item is updated.

    There is no notion of "unviewing".

    These updates should be performed in a transaction - with special care
    taken to ensure that the incremeting and decrementing of the cached counts
    is not prone to race conditions.
    """

    class Meta:
        unique_together = (
            "user",
            "content_item",
        )


class ContentItemQuestionnaire(Orderable):
    """
    A content item can have a questionnaire attached to it.

    This can be used to implement e.g post-module quizzes.
    """

    page = ParentalKey(ContentItem, related_name="questionnaires")

    class Meta:
        unique_together = (
            "page",
            # "document",
        )
