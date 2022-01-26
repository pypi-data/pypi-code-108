class VtexPrice:
    def __init__(self, listPrice=None,
                        costPrice=None,
                        markup=0):
            self.listPrice = listPrice
            self.costPrice = costPrice
            self.markup = markup

class VtexInventory:
    def __init__(self, unlimitedQuantity=False,
                        quantity=None):
            self.unlimitedQuantity = unlimitedQuantity
            self.quantity = quantity

class VtexImage:
    def __init__(self, IsMain=True,
                        Url='',
                        Name=None,
                        Label=None,
                        Text=None):
        self.IsMain = IsMain
        self.Url = Url
        if Name:
            self.Name = Name
        if Label:
            self.Label = Label
        if Text:
            self.Text = Text

class VtexSku:
    def __init__(self, Id=None,
                        ProductID=None,
                        IsActive=False,
                        Name='',
                        RefId='',
                        PackagedHeight=1,
                        PackagedLength=1,
                        PackagedWidth=1,
                        PackagedWeightKg=1,
                        Height=1,
                        Length=1,
                        Width=1,
                        WeightKg=1,
                        CubicWeight=1,
                        IsKit=False,
                        CreationDate='',
                        RewardValue=None,
                        EstimatedDateArrival=None,
                        ManufacturerCode='',
                        CommercialConditionId=1,
                        MeasurementUnit='',
                        UnitMultiplier=1,
                        ModalType=None,
                        KitItensSellApart=False,
                        price=None,
                        inventory=None,
                        images=[]):
        self.Id = Id
        self.ProductID = ProductID
        self.IsActive = IsActive
        self.Name = Name
        self.RefId = RefId
        self.PackagedHeight = PackagedHeight
        self.PackagedLength = PackagedLength
        self.PackagedWidth = PackagedWidth
        self.PackagedWeightKg = PackagedWeightKg
        self.Height = Height
        self.Length = Length
        self.Width = Width
        self.WeightKg = WeightKg
        self.CubicWeight = CubicWeight
        self.IsKit = IsKit
        self.CreationDate = CreationDate
        self.RewardValue = RewardValue
        self.EstimatedDateArrival = EstimatedDateArrival
        self.ManufacturerCode = ManufacturerCode
        self.CommercialConditionId = CommercialConditionId
        self.MeasurementUnit = MeasurementUnit
        self.UnitMultiplier = UnitMultiplier
        self.ModalType = ModalType
        self.KitItensSellApart = KitItensSellApart
        self.price = price
        self.inventory = inventory
        self.images = images

class VtexProduct:
    def __init__(self, Id=None,
                        Name='',
                        DepartmentId=1,
                        CategoryId=1,
                        BrandId=2000000,
                        LinkId='',
                        RefId='',
                        IsVisible=True,
                        Description='',
                        DescriptionShort='',
                        ReleaseDate='',
                        KeyWords='',
                        Title='',
                        IsActive=False,
                        TaxCode='',
                        MetaTagDescription='',
                        SupplierId=1,
                        ShowWithoutStock=False,
                        AdWordsRemarketingCode=None,
                        LomadeeCampaignCode=None,
                        Score=1,
                        skus=[]):
        self.Id = Id
        self.Name = Name
        self.DepartmentId = DepartmentId
        self.CategoryId = CategoryId
        self.BrandId = BrandId
        self.LinkId = LinkId
        self.RefId = RefId
        self.IsVisible = IsVisible
        self.Description = Description
        self.DescriptionShort= DescriptionShort
        self.ReleaseDate =ReleaseDate
        self.KeyWords = KeyWords
        self.Title = Title
        self.IsActive = IsActive
        self.TaxCode = TaxCode
        self.MetaTagDescription = MetaTagDescription
        self.SupplierId = SupplierId
        self.ShowWithoutStock = ShowWithoutStock
        self.AdWordsRemarketingCode = AdWordsRemarketingCode
        self.LomadeeCampaignCode = LomadeeCampaignCode
        self.Score = Score
        self.skus = skus

class VtexSpecification:
    Id: int
    SkuId: int
    FieldId: int
    FieldValueId: int
    Text: str

    def __init__(self, FieldId: int,
                        FieldValueId: int,
                        Id: int = None,
                        SkuId: int = None,
                        Text: str = None) -> None:
        self.FieldId = FieldId
        self.FieldValueId = FieldValueId
        if Id:
            self.Id = Id
        if SkuId:
            self.SkuId = SkuId
        if Text:
            self.Text = Text
