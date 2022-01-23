from django.db import models
import uuid

# Create your models here.


# class CargoType(models.Model):
#     grade = models.IntegerField(default=0, verbose_name="级别")
#     name = models.CharField(max_length=30, verbose_name="名称")
#     no = models.CharField(max_length=10, verbose_name="编号")
#     parent_type = models.ForeignKey('self', null=True, blank=True, verbose_name="父类目别", related_name="subClasses", on_delete=models.CASCADE)
#     if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
#
#     class Meta:
#         unique_together = ['parent_type', 'no']
#         verbose_name = "商品类别"
#         verbose_name_plural = verbose_name
#         db_table = "c_cargo_type"

class ServiceProvider(models.Model):
    """
    服务商
    """
    name = models.CharField(max_length=100, verbose_name="服务商企业名称", help_text="服务商企业名称")
    trade_code = models.CharField(max_length=100, verbose_name="企业编码", help_text="企业编码")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "服务商"
        verbose_name_plural = verbose_name
        db_table = "p_service_provider"
        managed = False

    def __str__(self):
        return self.id


class Cargo(models.Model):
    """
    货物
    """
    # 一体化
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, default='', verbose_name="商品料号", help_text="商品料号")
    hs_code = models.CharField(max_length=10, verbose_name="商品编码")
    ciq_code = models.CharField(max_length=10, verbose_name="商检编码", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="货名", help_text="货名")
    declare_elements = models.TextField(verbose_name="申报要素（商品规格型号、品牌）", default='', help_text="申报要素（商品规格型号、品牌）")
    source_area = models.CharField(max_length=50, default='', verbose_name="原产地（国）", help_text="原产地（国）")
    source_area_name = models.CharField(max_length=50, default='', verbose_name="原产地（国）名称", help_text="原产地（国）名称", null=True, blank=True)
    natcd = models.CharField(max_length=10, verbose_name="国别", help_text="国别", null=True, blank=True)
    natcd_name = models.CharField(max_length=10, verbose_name="国别名称", help_text="国别名称", null=True, blank=True)
    unit = models.CharField(max_length=20, verbose_name="数量单位", help_text="数量单位", null=True, blank=True)
    unit_name = models.CharField(max_length=20, verbose_name="数量单位名称", help_text="数量单位名称", null=True, blank=True)
    g_unit = models.CharField(max_length=20, verbose_name="申报单位", help_text="申报单位", null=True, blank=True)
    g_unit_name = models.CharField(max_length=20, verbose_name="申报单位名称", help_text="申报单位名称", null=True, blank=True)
    unit_1 = models.CharField(max_length=20, verbose_name="法定单位", help_text="法定单位", null=True, blank=True)
    unit_1_name = models.CharField(max_length=20, verbose_name="法定单位名称", help_text="法定单位名称", null=True, blank=True)
    unit_2 = models.CharField(max_length=20, verbose_name="法定第二单位", help_text="法定第二单位", null=True, blank=True)
    unit_2_name = models.CharField(max_length=20, verbose_name="法定第二单位名称", help_text="法定第二单位名称", null=True, blank=True)
    # wms
    # cargo_type = models.ForeignKey(CargoType, null=True, blank=True, verbose_name="类型", on_delete=models.CASCADE)
    image_path = models.ImageField(max_length=200, upload_to="cargo/images/", null=True, blank=True, verbose_name="图片地址")
    weight = models.DecimalField(verbose_name="重量/单位", null=True, blank=True, max_digits=10, decimal_places=4)
    volume = models.DecimalField(verbose_name="体积/单位", null=True, blank=True, max_digits=10, decimal_places=5)
    # tlms
    specs_quantity = models.DecimalField(max_digits=10, default=0, null=True, blank=True, decimal_places=2, verbose_name="规格量", help_text="规格量")
    specs_unit = models.CharField(max_length=100, default='', null=True, blank=True, verbose_name="规格单位", help_text="规格单位")
    pack_quantity = models.DecimalField(max_digits=10, default=0, null=True, blank=True, decimal_places=0, verbose_name="包装量", help_text="包装量")
    pack_unit = models.CharField(max_length=100, default='', null=True, blank=True, verbose_name="包装单位", help_text="包装单位")

    brand = models.CharField(max_length=50, null=True, blank=True, verbose_name="品牌", help_text="品牌")
    name_en = models.CharField(max_length=100, verbose_name="货物英文名", help_text="货物英文名", null=True, blank=True)
    gb_code = models.CharField(max_length=20, verbose_name="国标号", help_text="国标号", null=True, blank=True)
    common_name = models.CharField(max_length=40, verbose_name="通用名", help_text="通用名", null=True, blank=True)
    standard_name = models.CharField(max_length=40, verbose_name="标准名称", help_text="标准名称", null=True, blank=True)
    common_standard_type = models.CharField(max_length=50, verbose_name="通用标准中的类别名称", help_text="通用标准中的类别名称",
                                            null=True, blank=True)
    pack_type = models.CharField(max_length=50, verbose_name="包装类型", help_text="包装类型", null=True, blank=True)
    duty_rate = models.CharField(max_length=50, null=True, blank=True, verbose_name="DutyRate", help_text="DutyRate")
    if_automatic_license = models.BooleanField(default=True, verbose_name="是否需要自动进口许可证")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        # unique_together = ['code', 'hs_code', 'name', 'service_provider']
        verbose_name = "货物"
        verbose_name_plural = verbose_name
        db_table = "p_cargo"
        managed = False

    def __str__(self):
        return self.name


class Consignor(models.Model):
    """
    委托公司表（tlms-wms共用）
    """
    PAY_MODE = (
        (0, '现结'),
        (1, '月结'),
        (2, '海关')
    )
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    # tlms
    name = models.CharField(max_length=40, verbose_name="公司名称", help_text="公司名称")
    code = models.CharField(max_length=40, verbose_name="委托公司代码", help_text="委托公司代码")
    register_no = models.CharField(max_length=40, verbose_name="公司注册号", help_text="公司注册号")
    register_address = models.CharField(max_length=200, verbose_name="公司注册地址", help_text="公司注册地址")
    tax_id = models.CharField(max_length=40, verbose_name="税务登记号", help_text="税务登记号")
    bank_account = models.CharField(max_length=40, verbose_name="银行账号", help_text="银行账号")
    bank_name = models.CharField(max_length=40, verbose_name="开户行", help_text="开户行")
    invoice_title = models.CharField(max_length=500, verbose_name="发票抬头", help_text="发票抬头")
    contacts = models.CharField(max_length=40, verbose_name="联系人", help_text="联系人")
    contact_num = models.CharField(max_length=40, verbose_name="联系电话", help_text="联系电话")
    site_name = models.CharField(max_length=200, verbose_name="仓储场地名称", help_text="仓储场地名称", null=True, blank=True)
    site_address = models.CharField(max_length=200, verbose_name="仓储场地地址", help_text="仓储场地地址")
    # wms
    if_package_storehouse = models.BooleanField(default=False, verbose_name="是否包仓")
    pay_mode = models.IntegerField(choices=PAY_MODE, verbose_name="结费方式")
    if_customs = models.BooleanField(default=False, verbose_name="是否为海关")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['code', 'service_provider']
        verbose_name = "委托公司"
        verbose_name_plural = verbose_name
        db_table = "p_consignor"
        managed = False

    def __str__(self):
        return self.name


class DecMethod(models.Model):
    """
    申报方式（tlms）
    """
    name = models.CharField(max_length=40, verbose_name="方式名称", help_text="方式名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'service_provider']
        verbose_name = "申报方式"
        verbose_name_plural = verbose_name
        db_table = "p_dec_method"
        managed = False

    def __str__(self):
        return self.name


class WorkRoute(models.Model):
    """
    作业路线(tlms)
    """
    code = models.CharField(max_length=20, verbose_name="作业路线编码", help_text="作业路线编码")
    name = models.CharField(max_length=20, verbose_name="作业路线名称", help_text="作业路线名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['code', 'service_provider']
        verbose_name = "作业路线"
        verbose_name_plural = verbose_name
        db_table = "p_work_route"
        managed = False

    def __str__(self):
        return self.name


class CtnSize(models.Model):
    """
    箱尺寸
    """
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=4, verbose_name="尺寸名称", help_text="尺寸名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'service_provider']
        verbose_name = "箱尺寸"
        verbose_name_plural = verbose_name
        db_table = "p_ctn_size"
        managed = False

    def __str__(self):
        return self.name


class CtnType(models.Model):
    """
    箱类型
    """
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, verbose_name="类型代码", help_text="类型代码")
    name = models.CharField(max_length=10, verbose_name="类型名称", help_text="类型名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['code', 'service_provider']
        verbose_name = "箱类型"
        verbose_name_plural = verbose_name
        db_table = "p_ctn_type"
        managed = False

    def __str__(self):
        return self.name

IN_OR_OUTS = (
        ('集团内', '集团内'),
        ('集团外', '集团外')
)

class Supplier(models.Model):
    """
    供应商公司
    """
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40, verbose_name="公司名称", help_text="公司名称")
    code = models.CharField(max_length=40, verbose_name="客户代码", help_text="客户代码")
    register_no = models.CharField(max_length=40, verbose_name="公司注册号", help_text="公司注册号")
    register_address = models.CharField(max_length=200, verbose_name="公司注册地址", help_text="公司注册地址")
    tax_id = models.CharField(max_length=40, verbose_name="税务登记号", help_text="税务登记号")
    bank_account = models.CharField(max_length=40, verbose_name="银行账号", help_text="银行账号")
    bank_name = models.CharField(max_length=40, verbose_name="开户行", help_text="开户行")
    bank_no = models.CharField(max_length=40, verbose_name="银行编码", help_text="银行编码", null=True, blank=True)
    invoice_title = models.CharField(max_length=500, verbose_name="发票抬头", help_text="发票抬头")
    contacts = models.CharField(max_length=40, verbose_name="联系人", help_text="联系人")
    contact_num = models.CharField(max_length=40, verbose_name="联系电话", help_text="联系电话")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)
    in_or_out = models.CharField(choices=IN_OR_OUTS, default="集团外", null=True, blank=True, max_length=10)


    class Meta:
        verbose_name = "供应商公司"
        verbose_name_plural = verbose_name
        db_table = "p_supplier"
        managed = False

    def __str__(self):
        return self.name


class UnPackType(models.Model):
    """
    拆箱方式
    """
    CHARGE_MODE = (
        ('0', '按箱尺寸'),
        ('1', '按重量')
    )
    id = models.UUIDField(primary_key=True,  auto_created=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=4, unique=True,  verbose_name="拆箱方式")
    charge_mode = models.CharField(choices=CHARGE_MODE, max_length=1, default='0',  verbose_name="计费方式")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "拆箱方式"
        verbose_name_plural = verbose_name
        db_table = "p_unpack_type"
        managed = False

    def __str__(self):
        return self.name


class Forklift(models.Model):
    """
    叉车车辆
    """
    FORKLIFT_TYPE = (
        ('0', '堆高车'),
        ('1', '普通叉车'),
        ('2', '电动叉车')
    )
    no = models.CharField(max_length=30, verbose_name="编号")
    forklift_type = models.CharField(choices=FORKLIFT_TYPE, max_length=1, default='0', verbose_name="叉车车辆类型")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "叉车车辆"
        verbose_name_plural = verbose_name
        db_table = "p_forklift_type"
        managed = False


class TransMode(models.Model):
    """
    成交方式
    """
    code = models.CharField(max_length=30, verbose_name="编号")
    name = models.CharField(max_length=30, verbose_name="名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "成交方式表"
        verbose_name_plural = verbose_name
        db_table = "p_trans_mode"
        managed = False


class Currency(models.Model):
    """
    币制表
    """
    code = models.CharField(max_length=30, verbose_name="编号")
    name = models.CharField(max_length=30, verbose_name="名称")
    name_en = models.CharField(max_length=30, verbose_name="英文名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "币制表"
        verbose_name_plural = verbose_name
        db_table = "p_currency"
        managed = False


class TransportMode(models.Model):
    """
    运输方式
    """
    code = models.CharField(max_length=30, verbose_name="编号")
    name = models.CharField(max_length=30, verbose_name="名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "运输方式"
        verbose_name_plural = verbose_name
        db_table = "p_transport_mode"
        managed = False


class CustomsMode(models.Model):
    """
    关区表
    """
    code = models.CharField(max_length=30, verbose_name="编号")
    name = models.CharField(max_length=30, verbose_name="名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "关区表"
        verbose_name_plural = verbose_name
        db_table = "p_customs_mode"
        managed = False


class DomesticDestination(models.Model):
    """
    境内目的地
    """
    code = models.CharField(max_length=30, verbose_name="编号")
    name = models.CharField(max_length=30, verbose_name="名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "境内目的地"
        verbose_name_plural = verbose_name
        db_table = "p_domestic_destination"
        managed = False


class Country(models.Model):
    """
    国家地区代码表
    """
    code = models.CharField(max_length=30, verbose_name="地区编号")
    name = models.CharField(max_length=40, verbose_name="地区中文名称")
    name_en = models.CharField(max_length=40, verbose_name="地区英文名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "国家地区代码"
        verbose_name_plural = verbose_name
        db_table = "p_country"
        managed = False


class Measure(models.Model):
    """
    计量单位
    """
    unit = models.CharField(max_length=30, verbose_name="计量单位")
    unit_name = models.CharField(max_length=40, verbose_name="计量单位名称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "国计量单位"
        verbose_name_plural = verbose_name
        db_table = "p_measure"
        managed = False


class TradeMode(models.Model):
    """
    贸易方式
    """
    code = models.CharField(max_length=30, verbose_name="贸易方式编号")
    name = models.CharField(max_length=40, verbose_name="贸易方式全称")
    simple_name = models.CharField(max_length=40, verbose_name="贸易方式简称")
    if_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "贸易方式"
        verbose_name_plural = verbose_name
        db_table = "p_trade_mode"
        managed = False

