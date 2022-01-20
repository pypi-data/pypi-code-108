# -*- coding: utf-8 -*-
'''
原厂物料
FactoryMaterialItem 
FactoryCatergoryItem 
原厂资讯
FactoryNewsItem 
FactoryNewsMapItem 
FactoryNewsCategoryItem
原厂方案
FactoryPlanItem
FactoryCategoryItem
FactoryPlanMapItem
原厂课程视频
FactoryVideoItem
FactoryCourseItem
FactoryCourseCategoryItem
FactoryCourseMapItem
代理商
FactoryAgentItem
原厂pcnpdn
PCNPDNItem
原厂百科
FactoryBaikeItem
原厂价格
EbusinessPrice
'''
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
# 重要字段用'<----'标识,如果与需求不符合要找需求人对一下

#原厂物料
class FactoryMaterialItem(scrapy.Item):
    table = 'ware_detail' # 测试库bd-crawler 正式库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources=scrapy.Field()# 来源：oneyac-唯样，szlcsc-立创，datasheet5
    url=scrapy.Field()# 详情链接 <----
    title=scrapy.Field()  #型号  <----
    img_url=scrapy.Field() #图片链接,如果有多个会以 | 隔开  <----
    pdf_url=scrapy.Field() #pdf链接,如果有多个会以 | 隔开  <----
    category_name=scrapy.Field()  #分类名称  <----
    category_id=scrapy.Field()#xcc分类id  <---- {原厂英文名}_{分类英文名或者拼音(不要留空格)}
    brand_name=scrapy.Field() # 品牌名称
    brand_id=scrapy.Field()   #xcc品牌id
    descs=scrapy.Field()  #描述 <----
    container_json=scrapy.Field() #头的全部内容 
    other_url_json=scrapy.Field() #其他链接的json
    list_json=scrapy.Field()  #列表json <---- 参数数据json单层结构
    number=scrapy.Field() #总数量 
    spider_flag=scrapy.Field()#是否爬取当前url: 1是，0否,null否
    spider_number=scrapy.Field()  #已爬取数量
    create_time=scrapy.Field()#创建时间 <----
    creator=scrapy.Field()#创建人 <-----
    packing=scrapy.Field()#封装，同型号的多个用，号隔开 <----
    price_json=scrapy.Field() #价格json，格式如：[{"price":"1.2","qty":1}]
    mpq=scrapy.Field()#最小包装量
    moq=scrapy.Field()#最小起订量
    min_work_tp=scrapy.Field()#最低工作温度(单位摄氏度)
    max_work_tp=scrapy.Field()#最高工作温度(单位摄氏度)
    rough_weight=scrapy.Field()   #毛重(单位g)
    manner_packing=scrapy.Field() #包装方式
    layout_design=scrapy.Field()  #电路图
    other_pdf_url=scrapy.Field()  #其他规格书{"名称":"pdf链接"}
    raw_pdf_url = scrapy.Field()
    raw_img_url = scrapy.Field()


class FactoryMaterialItemMongo(scrapy.Item):
    table = 'ware_detail' # 测试库bd-crawler 正式库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources=scrapy.Field()# 来源：oneyac-唯样，szlcsc-立创，datasheet5
    url=scrapy.Field()# 详情链接 <----
    title=scrapy.Field()  #型号  <----
    img_url=scrapy.Field() #图片链接,如果有多个会以 | 隔开  <----
    pdf_url=scrapy.Field() #pdf链接,如果有多个会以 | 隔开  <----
    category_name=scrapy.Field()  #分类名称  <----
    category_id=scrapy.Field()#xcc分类id  <---- {原厂英文名}_{分类英文名或者拼音(不要留空格)}
    brand_name=scrapy.Field() # 品牌名称
    brand_id=scrapy.Field()   #xcc品牌id
    descs=scrapy.Field()  #描述 <----
    container_json=scrapy.Field() #头的全部内容 
    other_url_json=scrapy.Field() #其他链接的json
    list_json=scrapy.Field()  #列表json <---- 参数数据json单层结构
    number=scrapy.Field() #总数量 
    spider_flag=scrapy.Field()#是否爬取当前url: 1是，0否,null否
    spider_number=scrapy.Field()  #已爬取数量
    create_time=scrapy.Field()#创建时间 <----
    creator=scrapy.Field()#创建人 <-----
    packing=scrapy.Field()#封装，同型号的多个用，号隔开 <----
    price_json=scrapy.Field() #价格json，格式如：[{"price":"1.2","qty":1}]
    mpq=scrapy.Field()#最小包装量
    moq=scrapy.Field()#最小起订量
    min_work_tp=scrapy.Field()#最低工作温度(单位摄氏度)
    max_work_tp=scrapy.Field()#最高工作温度(单位摄氏度)
    rough_weight=scrapy.Field()   #毛重(单位g)
    manner_packing=scrapy.Field() #包装方式
    layout_design=scrapy.Field()  #电路图
    other_pdf_url=scrapy.Field()  #其他规格书{"名称":"pdf链接"}
    raw_pdf_url = scrapy.Field()
    raw_img_url = scrapy.Field()
    
class FactoryCatergoryItem(scrapy.Item):
    table = 'ware_category' # 测试库bd-crawler 正式库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field() #来源：oneyac-唯样，szlcsc-立创<-----
    url = scrapy.Field() #链接<-----
    level = scrapy.Field() #分类级别<-----
    category_name = scrapy.Field()#分类名称<-----
    en_name = scrapy.Field()#英文-分类名称
    category_id = scrapy.Field()#分类id<-----
    p_category_id = scrapy.Field()#父类-分类id<----- 如果没有父级不用写
    p_category_name = scrapy.Field()#父类-分类名称<-----
    children_number = scrapy.Field()#子类数量
    img_url = scrapy.Field()#图片链接 
    jsons = scrapy.Field()#额外参数 
    attrs = scrapy.Field()#属性名称列表 
    number = scrapy.Field()#总数量 
    spider_flag = scrapy.Field()#是否爬取当前url: 1是，0否
    spider_number = scrapy.Field()#已爬取数量
    spider_date = scrapy.Field()#爬虫年月日
    spider_time = scrapy.Field()#爬虫时间
    create_time = scrapy.Field()#创建时间
    creator = scrapy.Field()#创建人 <-----
    update_time = scrapy.Field()#更新时间
    updator = scrapy.Field()#更新人
    del_flag = scrapy.Field()#删除标记
    brand_name = scrapy.Field()#品牌名称 <-----
    brand_id = scrapy.Field()#xcc品牌id <-----

#原厂资讯
class FactoryNewsItem(scrapy.Item):
    table = 'news_detail' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    source =scrapy.Field() #*来源 <-----
    category =scrapy.Field() #*分类<-----
    source_url =scrapy.Field() #*来源链接<-----
    title =scrapy.Field() #*标题<-----
    content =scrapy.Field() #*内容<-----
    article_from =scrapy.Field() #*文章来源<-----
    author =scrapy.Field() #作者
    tips =scrapy.Field() #标签
    publish_time =scrapy.Field() #*新闻时间<-----
    create_time =scrapy.Field() #*创建时间<-----
    creator =scrapy.Field() #*创建人<-----
    update_time =scrapy.Field() #更新时间
    updator =scrapy.Field() #更新人
    spider_name =scrapy.Field() #爬虫名
    spider_time =scrapy.Field() #爬虫时间
    del_flag =scrapy.Field() #删除标记
    note =scrapy.Field() #备注
    img_url =scrapy.Field() #*图片链接(文章图片链接"|"做分割) <-----
    img_num =scrapy.Field() #用做图片数量(弃用不用写)
    new3 =scrapy.Field() #资讯是否公开(弃用不用写)
    abstract =scrapy.Field() #摘要
    read_number =scrapy.Field() #浏览次数(文章没有则随机2000以内) <-----
    is_open =scrapy.Field() #资讯是否公开(网信资讯设置为0) <----- 需要确认是否是网信资讯
    title_en =scrapy.Field() #英文标题 
    content_en =scrapy.Field() #英文内容
    tips_en =scrapy.Field() #英文标签
    is_en =scrapy.Field() #是否外文（0：否；1：是）(接口设置参数,不用写)
    appdetail_id =scrapy.Field() #uuid对应品牌id(品牌资讯需要,普通资讯不用写) <----- hash.sha1模式与原厂关联

class FactoryNewsMapItem(scrapy.Item): 
    table = 'app_detail_brand' #正式库/测试库bd-spider 
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    appdetail_id =scrapy.Field() #<-----
    brand_id = scrapy.Field() #<-----

class FactoryNewsCategoryItem(scrapy.Item):
    table = 'news_category'  # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field() #来源：cena
    url = scrapy.Field() #链接
    level = scrapy.Field() #分类级别
    category_name = scrapy.Field() #分类名称
    en_name = scrapy.Field() #英文-分类名称
    category_id = scrapy.Field() #分类id
    p_category_id = scrapy.Field() #父类-分类id
    p_category_name = scrapy.Field() #父类-分类名称
    p_number = scrapy.Field() #子类数量
    jsons = scrapy.Field() #额外参数
    attrs = scrapy.Field() #属性名称列表
    number = scrapy.Field() #总数量
    spider_flag = scrapy.Field() #是否爬取当前url: 1是，0否
    spider_number = scrapy.Field() #已爬取数量
    spider_date = scrapy.Field() #爬虫年月日
    spider_time = scrapy.Field() #爬虫时间
    create_time = scrapy.Field() #创建时间
    creator = scrapy.Field() #创建人
    update_time = scrapy.Field() #更新时间
    updator = scrapy.Field() #更新人
    del_flag = scrapy.Field() #删除标记

#原厂方案
class FactoryPlanItem(scrapy.Item):
    table = 'plan_info' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    name = scrapy.Field() # 名称 相当于资讯title  <-----
    style = scrapy.Field() # 分类 相当于资讯 sources <-----
    type_first = scrapy.Field() # 一级应用分类 相当于资讯 category_id <-----
    type_second = scrapy.Field() # 二级应用分类 相当于资讯 category_id <-----
    des = scrapy.Field() # 简介 列表页简介不可带html标签 
    detail_des = scrapy.Field() # 详细描述 相当于资讯的contain 正文内容 <-----
    image_url = scrapy.Field() # 图片资源 资源图片多张用|分割 <-----
    status = scrapy.Field() # 审批状态 
    time = scrapy.Field() # 发布时间 相当于资讯publish_time  <-----
    create_by_user = scrapy.Field() # 创建人  <-----
    create_datetime = scrapy.Field() # 创建时间 <-----
    scan_num = scrapy.Field() # 浏览次数  <-----
    collect_num = scrapy.Field() # 收藏次数 
    pdf_path = scrapy.Field() # pdf路径(设计下载) 
    related_documents_pdf = scrapy.Field() # 相关文档
    plan_url = scrapy.Field() # 方案链接 
    tips = scrapy.Field() # 标签 <-----
    no = scrapy.Field() # 编号，用于爬虫除重
    plan_id = scrapy.Field() # uuid,  用于关联品牌 <-----


class FactoryCategoryItem(scrapy.Item):
    table = 'plan_category' #正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    name = scrapy.Field() #一级分类名称 相当于资讯  <----- 展示字段
    type_first = scrapy.Field() #一级分类标识 相当于资讯 category_id <----- 关联字段 
    second_name = scrapy.Field() #二级分类名称 相当于资讯  <----- 展示字段
    type_second = scrapy.Field() #二级分类标识 相当于资讯 category_id <----- 关联字段 
    style = scrapy.Field() #分类 相当于资讯 sources <-----

class FactoryPlanMapItem(scrapy.Item):
    table = 'app_plan_brand'
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    plan_id = scrapy.Field() #uuid,  用于关联品牌 <-----
    brand_id = scrapy.Field() # 原厂id <-----

#原厂课程视频
class FactoryVideoItem(scrapy.Item):
    table = 'app_video' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    title = scrapy.Field() # 标题 <-----
    source = scrapy.Field() # 来源 <-----
    publishtime = scrapy.Field() # 发布时间 <-----
    link_address = scrapy.Field() # 本地链接地址 <-----
    is_checked = scrapy.Field() # 是否审核，默认0未审核，1 审核 
    create_time = scrapy.Field() # 创建时间 <-----
    creator = scrapy.Field() # 创建人 <-----
    is_deleted = scrapy.Field() # 是否删除 0删除，1 不删除
    course_url = scrapy.Field() # 课程url,映射父级用处 <----- 关联字段
    original_url = scrapy.Field() # 原链接 <-----
    sort = scrapy.Field() # 排序 视频课程的序列号,如:课时二 写2 (int类型) <-----

class FactoryCourseItem(scrapy.Item):
    table = 'app_course' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    category_id = scrapy.Field() #分类ID 
    course_name = scrapy.Field() #课程名
    snapshot = scrapy.Field() #缩略图 <-----课程图片,详情页中取或者列表页取
    introduction = scrapy.Field() #介绍 <-----课程介绍
    source = scrapy.Field() #来源 <-----
    publishtime = scrapy.Field() #发布日期 <-----
    is_checked = scrapy.Field() #是否审核，默认0未审核，1已审核
    create_time = scrapy.Field() #创建时间 <-----
    creator = scrapy.Field() #创建人 <-----
    tips = scrapy.Field() #标签 <-----
    author_intro = scrapy.Field() #作者简介 <-----
    course_url = scrapy.Field() #课程url,映射video作用 <----- 详情表关联字段
    category_url = scrapy.Field() #分类url,映射课程分类作用 <----- 父级关联字段
    course_id = scrapy.Field() #课程UUID <-----hash.sha1模式 用于关联品牌


class FactoryCourseCategoryItem(scrapy.Item):
    table = 'app_course_category' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    category_name = scrapy.Field() #分类名称 <-----
    create_time = scrapy.Field() #创建时间 <-----
    creator = scrapy.Field() #创建人 <-----
    category_url = scrapy.Field() #分类url,映射课程作用 <-----
    sort = scrapy.Field() #排序 <-----

class FactoryCourseMapItem(scrapy.Item):
    table = 'app_course_brand' # 正式库/测试库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    course_id = scrapy.Field() #uuid,  用于关联品牌 <-----
    brand_name = scrapy.Field() # 原厂id <-----

#代理商
class FactoryAgentItem(scrapy.Item):
    table = 'app_agent_copy1'
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')} 
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    brand_id = scrapy.Field() #品牌ID
    brand_name_cn = scrapy.Field() #品牌中文名称
    brand_name_en = scrapy.Field() #品牌英文名称
    group_name = scrapy.Field() #分组名称
    agent_name = scrapy.Field() #代理商中文名称
    email = scrapy.Field() #邮箱
    phone = scrapy.Field() #电话号码
    country = scrapy.Field() #国家
    city = scrapy.Field() #城市
    address = scrapy.Field() #地址
    create_time = scrapy.Field() #创建时间

# PCN/PDN
class PCNPDNItem(scrapy.Item):
    table = 'pcn_pdn_new'
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field() # 来源,原厂Manufacturers
    type = scrapy.Field()   # 必填，格式PCN或PDN <----
    title = scrapy.Field()  # 必填，型号<----
    brand_name = scrapy.Field()  # 必填，品牌名<----
    pdf_file = scrapy.Field()# 必填，PCN/PDN链接文件<----
    pdf_url = scrapy.Field()   # 必填,pdf链接
    brand_id = scrapy.Field()   # 必填,品牌id
    creator = scrapy.Field()  # 创建人
    create_time = scrapy.Field()  # 创建时间
    update_time = scrapy.Field()  # 更新时间
    change_content = scrapy.Field()   # 变更内容
    no = scrapy.Field()  # 编码

class FactoryBaikeItem(scrapy.Item):
    table = 'ware_wiki'
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field()  # 来源：oneyac-唯样，szlcsc-立创，datasheet5
    url = scrapy.Field()  # 详情链接 <----
    title = scrapy.Field()  # 型号  <----
    brand_name = scrapy.Field()
    brand_id = scrapy.Field()  # xcc品牌id <-----
    category_name = scrapy.Field()  # 分类名称  <----
    category_id = scrapy.Field()  # xcc分类id  <---- {原厂英文名}_{分类英文名或者拼音(不要留空格)}
    create_time = scrapy.Field()  # 创建时间 <----
    creator = scrapy.Field()  # 创建人 <-----
    application = scrapy.Field()  # 应用 <-----
    feature = scrapy.Field()  # 特点特性 <-----
    standard = scrapy.Field()  # 规格 <-----
    description = scrapy.Field()  # 描述 <-----
    overview = scrapy.Field()  # 概述 <-----

class EbusinessPrice(scrapy.Item):
    table = 'ware_detail_price'  # 测试库bd-crawler 正式库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field()  # 来源：oneyac-唯样，szlcsc-立创，datasheet5
    url = scrapy.Field()  # 详情链接 <----
    title = scrapy.Field()  # 型号  <----
    unit = scrapy.Field()  # CNY(人民币)标识为0 USD(美元)标识为1 <----
    price_json = scrapy.Field()  # 价格
    brand_id = scrapy.Field()  # 品牌ID
    stock = scrapy.Field()  # 库存数量  <----
    in_stock = scrapy.Field()  # 是否有货  0无货 1有货
    brand_name = scrapy.Field()  # <----厂商

class officeItem(scrapy.Item):
    table = 'app_office'
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params) 
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    sources = scrapy.Field()  # <---数据来源,取网站域名
    brand_name = scrapy.Field()  #   品牌名称
    name = scrapy.Field()     #  <---办事处名称
    mobile = scrapy.Field()   #   <--- 办事处电话
    address = scrapy.Field()   #  <--- 办事处地址
    agency_id = scrapy.Field()   #  <--- 代理商id
    email = scrapy.Field()  # <--- 办事处地址
    city = scrapy.Field()  # <--- 城市信息
    country = scrapy.Field()  # <--- 国家
    create_time = scrapy.Field()  # <--- 创建时间

if __name__=='__main__':
    item = officeItem(table = 'plan_info',table_add = '_yongjie')
    print(item.table)
    item = officeItem(table_add = '_yongjie')
    print(item.table)
    item = officeItem(table = 'plan_info')
    print(item.table)
    item = officeItem()
    print(item.table)
    item['city'] = 'shanghai'
    print(item['city'])