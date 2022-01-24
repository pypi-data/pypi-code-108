from django.http import JsonResponse
from ..serializer import Serializer
from ..paginator import PaginatorBase
from ..filters import Filter


class APIViewMeta(type):

    def __init__(cls, name, bases, act):
        super().__init__(name, bases, act)
        cls.const(name, bases, act)

    def const(cls, name, bases, act):
        if '_base' in act and act['_base']:
            return
        filter_class = getattr(cls, 'filter_class')
        serializer_class = getattr(cls, 'serializer_class')
        paginator_class = getattr(cls, 'paginator_class')
        process_queryset = getattr(cls, 'process_queryset')

        # filter_class为None时，必须要定义process_queryset函数
        if not filter_class and process_queryset == APIView.process_queryset:
            raise ValueError('{}:filter_class为None时，必须要定义process_queryset函数，'
                             '且process_queryset不能返回None'.format(name))
        if not serializer_class:
            raise TypeError('{}没有配置serializer_class！'.format(name))

        if not issubclass(serializer_class, Serializer):
            raise TypeError('{}的serializer_class类型错误！'.format(name))

        if filter_class and not issubclass(filter_class, Filter):
            raise TypeError('{}的filter_class类型错误！'.format(name))

        if paginator_class and not issubclass(paginator_class, PaginatorBase):
            raise TypeError('{}的paginator_class类型错误！'.format(name))


class APIView(metaclass=APIViewMeta):
    _base = True  # _base=True意味着该类只作被继承使用，不会在业务中直接使用
    # filter_class为None时，一定要定义process_queryset函数，且process_queryset不能返回None
    filter_class = None
    paginator_class = None
    serializer_class = None

    def __init__(self):
        self.request = None
        self.queryset = None
        self.results = []  # 理论上results的数据类型是可变类型(列表或者字典)，意味着可以原地修改，但不确定！
        self.page_count = {}

    def _filter(self):
        """过滤，从request中获取查询条件(query),
        如果process_queryset返回的queryset为None,queryset就是filter_class中的Meta.model.objects.all()"""
        if self.filter_class:
            self.queryset = self.filter_class(self.request, self.queryset)

    def _paginator(self):
        if not self.paginator_class:
            return
        paginator = self.paginator_class(self.queryset, self.request)
        self.queryset = paginator.sub_set()
        self.page_count = paginator.page_count()

    def _serializer(self):
        self.results = self.serializer_class(self.queryset)
        # 钩子函数处理result
        self.results = self.process_results(self.results)

    def _json_response(self):
        """生成最终数据，可以被序列化的数据"""
        if self.paginator_class:
            data = {'results': self.results}
            data.update(self.page_count)
        else:
            data = self.results
        # data拦截函数,处理最终的data数据
        data = self.process_data(self.request, data)
        return JsonResponse(data, safe=False)

    def process_request(self, request):
        """拦截处理request"""
        pass

    def process_queryset(self, request):
        """process_queryset需要返回一个queryset,
        该函数在过滤操作之前运行，如果返回了一个queryset，过滤函数会从这个queryset中过滤出结果，
        如果没有定义该函数，或者该函数返回None，queryset就是过滤类中的Meta.model.objects.all()
        可以在该函数中引发异常，使接口返回400错误，表示资源不可访问或不存在。
        注意：
            1.process_queryset不能对queryset进行切片等破坏性操作，否则会导致过滤出错！
            2.当process_queryset未定义或返回None时, filter_class一定不能为None！
        """
        return self.queryset

    def process_results(self, results):
        """results的拦截函数，可以重写该函数对results 进行修改
        results是序列化后的结果，results一般是由多个字典对象组成的列表或者一个单独的字典"""
        return results

    def process_data(self, request, data):
        """data拦截函数，data是接口返回给请求的最终数据"""
        return data

    @classmethod
    def as_view(cls):
        def api(request):
            self = cls()
            return self.api(request)

        return api

    def api(self, request):
        """直接暴露给路由的API接口"""
        self.request = request
        self.process_request(self.request)  # 处理request
        # 处理queryset
        try:
            self.queryset = self.process_queryset(self.request)
        except Exception as err:
            return JsonResponse({'msg': '资源不可访问，或不存在！', 'errors': str(err)}, status=400)
        try:
            self._filter()  # 过滤
        except ValueError as err:
            return JsonResponse({'msg': '查询参数错误！', 'errors': str(err)}, status=400)
        self._paginator()  # 可能需要的翻页
        self._serializer()  # 序列化结果到self.results
        return self._json_response()
