from django.db.models import (
    CASCADE,
    PROTECT,
    CharField,
    DateField,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    TextField,
)

from m3_db_utils.models import (
    TitledModelEnum,
)

from web_bb.core.documents.enums import (
    DocumentEnum,
)


class BaseElectronicDocumentStatus(TitledModelEnum):
    """
    Базовая модель-перечесление статусов электронных документов
    """

    class Meta:
        abstract = True


class BaseElectronicDocumentTransitionPermission(TitledModelEnum):
    """
    Базовая модель  перечисление для описания правил доступа к функциям перехода статусов
    """

    abbreviation = CharField(verbose_name='Сокращение', max_length=256)

    class Meta:
        abstract = True


class BaseElectronicDocumentKind(TitledModelEnum):
    """
    Базовая модель вида документа
    """

    pack_code = CharField(
        verbose_name='Пак вида документа',
        max_length=128,
        choices=DocumentEnum.get_choices(),
        blank=True,
        null=True,
    )

    doc_num_auto = BooleanField(
        verbose_name='Признак необходимости генерации номера документа',
        default=False,
    )

    class Meta:
        abstract = True


class BaseElectronicDocument(Model):
    """
    Базовая модель электронного документа
    """

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentStatus
    status = ForeignKey(
        to=BaseElectronicDocumentStatus,
        verbose_name='Статус',
        on_delete=PROTECT,
    )

    number = PositiveIntegerField(
        verbose_name='Номер',
    )

    date = DateField(
        verbose_name='Дата',
    )

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentKind
    document_kind = ForeignKey(
        to=BaseElectronicDocumentKind,
        verbose_name='Вид документа',
        on_delete=PROTECT,
    )

    class Meta:
        abstract = True


class BaseElectronicDocumentTransition(Model):
    """
    Переход электронного документа в новый статус
    """

    title = CharField(
        verbose_name='Наименование перехода',
        max_length=256,
    )

    icon_class = CharField(
        verbose_name='CSS класс добавления иконки кнопки перехода',
        max_length=256,
    )

    info_text = TextField(
        verbose_name='Текст информационного сообщения перехода',
        max_length=2048,
    )

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentTransitionPermission
    permission = ForeignKey(
        to=BaseElectronicDocumentTransitionPermission,
        verbose_name='Право осуществления перехода',
        on_delete=PROTECT,
    )

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentStatus. В случае создания документа, он может быть создан без функции с отсутствием
    # начального статуса
    from_status = ForeignKey(
        to=BaseElectronicDocumentStatus,
        verbose_name='Статус до перехода',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentStatus
    to_status = ForeignKey(
        to=BaseElectronicDocumentStatus,
        verbose_name='Статус после перехода',
        on_delete=PROTECT,
    )

    # В случае создания документа, он может быть создан без указания функции с отсутствием
    # начального статуса
    function_pack = CharField(
        verbose_name='Пак функции',
        max_length=128,
        blank=True,
        null=True,
    )

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentKind
    document_kind = ForeignKey(
        to=BaseElectronicDocumentKind,
        verbose_name='Вид документа',
        on_delete=PROTECT,
    )

    class Meta:
        abstract = True


class BaseElectronicDocumentEditingLog(Model):
    """
    Базовая модель хранения лога смены статуса электронного документа
    """

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocument
    document = ForeignKey(
        to=BaseElectronicDocument,
        verbose_name='Электронный документ',
        on_delete=CASCADE,
    )

    user = ForeignKey(to='auth.User', verbose_name='Пользователь', on_delete=PROTECT)

    # Поле должно быть переопредено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocumentTransition
    transition = ForeignKey(
        to=BaseElectronicDocumentTransition,
        verbose_name='Осуществленный переход',
        on_delete=PROTECT,
    )

    notice = TextField(
        verbose_name='Примечание',
        max_length=1024,
    )

    created_at = DateTimeField(verbose_name='Дата и время внесения изменений', auto_now_add=True)

    class Meta:
        abstract = True


class BaseElectronicDocumentAttachment(Model):
    """
    Связанный файл
    """

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocument
    document = ForeignKey(
        to=BaseElectronicDocument,
        verbose_name='Электронный документ',
        on_delete=CASCADE,
    )

    # Поле лучше переопределить у потомка с указанием корректного места сохранения файла
    link = FileField(
        verbose_name='Загружаемый файл',
        upload_to='edm/%Y/%m/%d',
    )

    created_at = DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class BaseElectronicDocumentElectronicSignature(Model):
    """
    Электронная подпись электронного документа
    """

    # Поле должно быть переопределено у потомка с использованием реальной модели статуса наследника
    # BaseElectronicDocument
    document = ForeignKey(
        to=BaseElectronicDocument,
        verbose_name='Электронный документ',
        on_delete=CASCADE,
    )

    signer = ForeignKey(
        to='auth.User',
        verbose_name='Подписант',
        on_delete=PROTECT,
    )

    # Поле лучше переопределить у потомка с указанием корректного места сохранения файла
    file_link = FileField(
        verbose_name='Подписанный файл',
        upload_to='edm_signed_files/%Y/%m/%d',
    )

    # Поле лучше переопределить у потомка с указанием корректного места сохранения файла
    archive_link = FileField(
        verbose_name='Архив с файлом и подписью',
        upload_to='edm_signed_files/%Y/%m/%d',
    )

    signature = TextField(
        verbose_name='ЭЦП',
    )

    certificate_thumbprint = CharField(
        verbose_name='Отпечаток сертификата',
        max_length=40,
    )
    certificate_serial_number = CharField(
        verbose_name='Серийный номер сертификата',
        max_length=40,
    )

    notice = TextField(
        verbose_name='Комментарий',
        max_length=1024,
    )

    signed_at = DateTimeField(
        verbose_name='Дата и время подписания',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
