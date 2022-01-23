from datetime import datetime
import random

from django.db import models

# Create your models here.123
from ..tlms_wms_public_table.models import Consignor, Cargo, ServiceProvider, CtnSize, CtnType


class TlmsWmsEntDirectField(models.CharField):
    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super(TlmsWmsEntDirectField, self).__init__(max_length=max_length, *args, **kwargs)

    def db_type(self, connection):
        return 'char(%s)' % self.max_length


def tlms_wms_ent_direct_id():
    """
    Generate a random id
    定义一个自增主键函数，在每次创建的时候都会调用
    """
    now_time = datetime.now().strftime('%y%m%d%H%M%S')
    default = 'TLMS-WMS-RK' + now_time + str(random.choice(range(100, 999)))
    return default


class TlmsWmsEntDirect(models.Model):
    """
    委托入库指令
    """
    status = (
        (1, '已下发 | 未接受'),
        (2, '已接收 | 已接受'),
        (3, '已完成 | 已完成'),
    )
    stock_bill = (
        (1, '进库'),
        (2, '出库'),
    )
    stock = (
        (1, '保税'),
        (2, '非保税'),
    )
    bill = (
        (1, '一线'),
        (2, '二线'),
        (3, '区内'),
        (4, '区间')
    )
    business = (
        (1, '自用设备'),
        (2, '简单加工'),
        (3, '保税加工'),
        (4, '保税仓储'),
        (5, '转口贸易'),
        (6, '跨境电商'),
        (7, '汽车平行进口'),
        (8, '融资租赁'),
        (9, '期货保税交割'),
        (10, '保税维修'),
        (11, '进口汽车保税存储'),
        (12, '保税研发'),
        (13, '委托加工'),
        (14, '大宗商品现货保税交易'),
    )
    classify = (
        ('I', '料件'),
        ('E', '成品'),
    )
    dclcus = (
        (1, '报关'),
        (2, '非报关'),
    )
    id = TlmsWmsEntDirectField(max_length=26, primary_key=True, auto_created=True, default=tlms_wms_ent_direct_id, editable=False)
    tlms_plan = models.CharField(max_length=30, null=True, blank=True, verbose_name="tlms计划号", help_text="tlms计划号")
    wms_ent_plan = models.CharField(max_length=30, null=True, blank=True, verbose_name="wms入库计划号", help_text="wms入库计划号")
    wms_out_plan = models.CharField(max_length=30, null=True, blank=True, verbose_name="wms出库计划号", help_text="wms出库计划号")
    plan_status = models.SmallIntegerField(choices=status, default=0, verbose_name="计划状态", help_text="计划状态")
    # 共用 一体化
    stock_bill_type = models.SmallIntegerField(choices=stock_bill, default=1, verbose_name="进出类型", help_text="进出类型")
    bill_type = models.SmallIntegerField(choices=bill, default=1, verbose_name="出入库类型", help_text="出入库类型")
    stock_type = models.SmallIntegerField(choices=stock, default=1, verbose_name="库存类型", help_text="库存类型")
    b_l_no = models.CharField(max_length=30, verbose_name="提单号", help_text="提单号", null=True, blank=True)
    consignor = models.ForeignKey(Consignor, on_delete=models.CASCADE, verbose_name="委托公司", help_text="委托公司")
    total_quantity = models.IntegerField(verbose_name="总数量（件数）", help_text="总数量（件数）", default=0)
    total_gross_weight = models.DecimalField(verbose_name="毛重", default=0, max_digits=10, decimal_places=2)
    total_net_weight = models.DecimalField(verbose_name="净重", default=0, max_digits=10, decimal_places=2)
    business_type = models.SmallIntegerField(choices=business, default=14, verbose_name="业务类别", help_text="业务类别")
    classify_type = models.CharField(choices=classify, default='E', max_length=1, verbose_name="料件成品标志",
                                     help_text="料件成品标志")
    supv_mode = models.CharField(max_length=30, verbose_name="监管方式", help_text="监管方式", null=True, blank=True)
    traf_mode = models.CharField(max_length=30, verbose_name="运输方式", help_text="运输方式", null=True, blank=True)
    i_e_port = models.CharField(max_length=30, verbose_name="进出境关别", help_text="进出境关别", null=True, blank=True)
    custome_code = models.CharField(max_length=30, verbose_name="主管海关", help_text="主管海关", null=True, blank=True)
    dclcus_flag = models.SmallIntegerField(choices=dclcus, default=1, verbose_name="报关标志", help_text="报关标志")
    customs_dec_no = models.CharField(max_length=30, verbose_name="报关单号", help_text="报关单号", null=True, blank=True)
    destination_code = models.CharField(max_length=30, verbose_name="最终目的国代码（地区）", help_text="最终目的国代码（地区）", null=True,
                                        blank=True)
    stship_trsarv_code = models.CharField(max_length=30, verbose_name="启运国/运抵国代码（地区）", help_text="启运国/运抵国代码（地区）",
                                          null=True, blank=True)
    district_code = models.CharField(max_length=30, verbose_name="境内目的地/货源地代码", help_text="境内目的地/货源地代码", null=True,
                                     blank=True)
    trade_country_code = models.CharField(max_length=30, verbose_name="贸易国代码（地区）", help_text="贸易国代码（地区）", null=True,
                                          blank=True)
    rlt_entry_no = models.CharField(max_length=64, verbose_name="关联报关单（备案清单、简易申报单）编号", help_text="关联报关单（备案清单、简易申报单）编号",
                                    null=True, blank=True)
    rlt_invt_no = models.CharField(max_length=64, verbose_name="关联保税核注清单编号", help_text="关联保税核注清单编号", null=True,
                                   blank=True)
    owner_name = models.CharField(max_length=256, verbose_name="货主名称", help_text="货主名称", null=True, blank=True)
    stock_date = models.DateField(verbose_name="创建时间", help_text="创建时间", auto_now_add=True)
    lastupdatedt = models.DateField(verbose_name="数据最后更新时间", help_text="数据最后更新时间", auto_now=True)
    pass_time = models.DateField(verbose_name="放行时间", help_text="放行时间", null=True, blank=True)
    transit_time = models.DateField(verbose_name="核放时间", help_text="核放时间", null=True, blank=True)
    # tlms
    contract_no = models.CharField(max_length=30, verbose_name="合同号/订单号", help_text="合同号/订单号")
    dec_method = models.CharField(max_length=30, verbose_name="申报方式", help_text="申报方式", null=True, blank=True)
    work_route = models.CharField(max_length=30, verbose_name="作业路线", help_text="作业路线", null=True, blank=True)
    js_no = models.CharField(max_length=30, verbose_name="js备案号", help_text="js备案号", null=True, blank=True)
    source_port = models.CharField(max_length=50, verbose_name="起运港", help_text="起运港", null=True, blank=True)
    vessel = models.CharField(max_length=30, verbose_name="船名", help_text="船名", null=True, blank=True)
    voyage = models.CharField(max_length=30, verbose_name="航次", help_text="航次", null=True, blank=True)
    aim_port = models.CharField(max_length=30, verbose_name="目的港", help_text="目的港", null=True, blank=True)
    inspection_no = models.CharField(max_length=30, verbose_name="报检号", help_text="报检号", null=True, blank=True)
    trade_mode = models.CharField(max_length=50, verbose_name="贸易方式", help_text="贸易方式", null=True, blank=True)
    package_type = models.CharField(max_length=50, verbose_name="包装种类", help_text="包装种类", null=True, blank=True)
    transaction_mode = models.CharField(max_length=50, verbose_name="成交方式", help_text="成交方式", null=True, blank=True)
    est_arrival_time = models.DateField(verbose_name="预计到港日期", help_text="预计到港日期", null=True, blank=True)
    arrival_time = models.DateField(verbose_name="到港日期", help_text="到港日期", null=True, blank=True)
    sender = models.CharField(max_length=100, verbose_name="发货人", null=True, blank=True)
    receiver = models.CharField(max_length=100, verbose_name="收货人", null=True, blank=True)
    # wms
    remark = models.CharField(max_length=200, verbose_name="备注", help_text="备注", null=True, blank=True)
    plan_ent_date = models.DateTimeField(verbose_name="出入库时间")
    if_buckle_cargo = models.BooleanField(default=False, verbose_name="是否海关扣货")
    service_provider = models.ForeignKey(ServiceProvider, verbose_name="服务企业", on_delete=models.CASCADE)
    # sender = models.CharField(max_length=10, default='', verbose_name="指令下发人")
    # send_datetime = models.DateTimeField(default=datetime.now, verbose_name="指令下发时间")
    # receriver = models.CharField(max_length=10, default='', verbose_name="指令接收人")
    # recerive_datetime = models.DateTimeField(null=True, blank=True, verbose_name="指令接收时间")

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.sender = self.
    #     else:
    #         self.u_user = self.user
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = "委托入库指令"
        verbose_name_plural = verbose_name
        db_table = "tlms_wms_ent_direct"
        managed = False

    def __str__(self):
        return self.b_l_no


class TlmsWmsEntDetailIdField(models.CharField):
    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super(TlmsWmsEntDetailIdField, self).__init__(max_length=max_length, *args, **kwargs)

    def db_type(self, connection):
        return 'char(%s)' % self.max_length


class TlmsWmsEntDetails(models.Model):
    """
    委托入库货物明细
    """
    id = TlmsWmsEntDetailIdField(max_length=17, primary_key=True, auto_created=True, editable=False)
    # 一体化
    ent_direct = models.ForeignKey(TlmsWmsEntDirect, verbose_name="入库指令", related_name='ent_direct_details',
                                 on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, verbose_name="货物", on_delete=models.CASCADE)
    wms_ent_plan = models.CharField(max_length=30, null=True, blank=True, verbose_name="wms入库计划号",
                                    help_text="wms入库计划号/出库时必填")
    bill_detail_seqno = models.CharField(max_length=64, verbose_name="出入库单明细序号", help_text="出入库单明细序号", null=True,
                                         blank=True)
    entry_gds_seqno = models.CharField(max_length=64, verbose_name="关联报关单（备案清单、简易申报单）商品序号",
                                       help_text="关联报关单（备案清单、简易申报单）商品序号", null=True, blank=True)
    qty = models.DecimalField(verbose_name="申报数量", default=0, max_digits=19, decimal_places=5)
    qty_1 = models.DecimalField(verbose_name="法定数量", default=0, max_digits=19, decimal_places=5)
    qty_2 = models.DecimalField(verbose_name="法定第二数量", default=0, max_digits=19, decimal_places=5)
    unit_price = models.DecimalField(verbose_name="单价", default=0, max_digits=19, decimal_places=5)
    total_price = models.DecimalField(verbose_name="总价", default=0, max_digits=19, decimal_places=5)
    trade_curr = models.CharField(max_length=10, verbose_name="币值", help_text="币值", null=True, blank=True)
    net_wt = models.DecimalField(verbose_name="实际净重", default=0, max_digits=19, decimal_places=5)
    gross_wt = models.DecimalField(verbose_name="实际毛重", default=0, max_digits=19, decimal_places=5)
    volume = models.DecimalField(verbose_name="实际体积", default=0,  max_digits=19, decimal_places=5)
    amount = models.IntegerField(verbose_name="实际数量", default=0)
    pellet_amount = models.IntegerField(verbose_name="实际托盘数量", default=0)
    lastupdatedt = models.DateField(verbose_name="数据最后更新时间", help_text="数据最后更新时间", auto_now=True)
    # tlms
    mark = models.CharField(max_length=20, verbose_name="批次/唛头")
    factory_no = models.CharField(max_length=30, null=True, blank=True,  verbose_name="工厂编号", help_text="工厂编号")
    plan_amount = models.IntegerField(verbose_name="计划数量", default=0)
    plan_net_wt = models.DecimalField(verbose_name="计划净重", default=0, max_digits=19, decimal_places=5)
    plan_gross_wt = models.DecimalField(verbose_name="计划毛重", default=0, max_digits=19, decimal_places=5)
    plan_volume = models.DecimalField(verbose_name="计划体积", default=0, max_digits=10, decimal_places=5)
    plan_pellet_amount = models.IntegerField(verbose_name="计划托盘数量", default=0, null=True, blank=True)
    produced_date = models.DateField(verbose_name="生产日期", null=True, blank=True, help_text="生产日期")
    # tlms
    ed = models.DateField(verbose_name="有效日期", help_text="有效日期", null=True, blank=True)
    # wms
    remark = models.CharField(max_length=255, null=True, blank=True,  verbose_name="备注")

    class Meta:
        verbose_name = "入库计划明细"
        verbose_name_plural = verbose_name
        db_table = "ent_direct_detail"
        managed = False


class TlmsWmsEntCtnIdField(models.CharField):
    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super(TlmsWmsEntCtnIdField, self).__init__(max_length=max_length, *args, **kwargs)

    def db_type(self, connection):
        return 'char(%s)' % self.max_length


class TlmsWmsEntCtn(models.Model):
    """
    委托业务箱子明细
    """
    id = TlmsWmsEntCtnIdField(max_length=18, primary_key=True, auto_created=True, editable=False)
    ent_direct = models.ForeignKey(TlmsWmsEntDirect, on_delete=models.CASCADE, related_name='ent_direct_ctn',
                                 verbose_name="订单号", help_text="订单号")
    ctnno = models.CharField(max_length=30, verbose_name="箱号", help_text="箱号")
    ctn_size = models.ForeignKey(CtnSize, on_delete=models.CASCADE, related_name='ent_direct_ctn_size', verbose_name="箱尺寸", help_text="箱尺寸")
    ctn_type = models.ForeignKey(CtnType, on_delete=models.CASCADE, related_name='ent_direct_ctn_type', verbose_name="箱类型", help_text="箱类型")
    seal_no = models.CharField(max_length=30, verbose_name="铅封号", help_text="铅封号", null=True, blank=True)
    gross_weight = models.DecimalField(verbose_name="箱毛重", help_text="箱毛重", default=0, max_digits=19,
                                       decimal_places=5)
    remark = models.CharField(max_length=200, verbose_name="备注", help_text="备注", null=True, blank=True)

    class Meta:
        verbose_name = "委托业务箱子明细"
        verbose_name_plural = verbose_name
        db_table = "ent_direct_ctn"
        managed = False

    def __str__(self):
        return self.ctnno


class TlmsWmsCtnDetail(models.Model):
    """
    箱子-货物-关系表
    """
    ent_direct_id = models.CharField(max_length=50, verbose_name="订单号", help_text="订单号")

    ent_direct_detail = models.ForeignKey(TlmsWmsEntDetails, on_delete=models.CASCADE, related_name='ctncargo_details',
                                          verbose_name="货名", help_text="货名")
    ent_direct_ctn = models.ForeignKey(TlmsWmsEntCtn, on_delete=models.CASCADE, related_name='ctncargo_ctn'
                                       , verbose_name="箱号", help_text="箱号", null=True, blank=True)
    quantity = models.IntegerField(verbose_name="数量", help_text="数量", default=0)
    gross_weight = models.DecimalField(verbose_name="箱毛重", help_text="箱毛重", default=0, max_digits=10,
                                       decimal_places=5)
    net_weight = models.DecimalField(verbose_name="净量", default=0, max_digits=10, decimal_places=5)
    volume = models.DecimalField(verbose_name="体积", default=0, max_digits=10, decimal_places=5)

    class Meta:
        verbose_name = "箱子-货物-关系表"
        verbose_name_plural = verbose_name
        db_table = "tlms_wms_ctn_cargo"
        managed = False

    def __str__(self):
        return str(self.ent_direct_id)


