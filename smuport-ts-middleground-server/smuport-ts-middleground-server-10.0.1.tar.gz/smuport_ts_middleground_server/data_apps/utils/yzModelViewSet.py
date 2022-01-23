from rest_framework import viewsets
from rest_framework.response import Response


def resp():
    res = {
        'code': 0,
        'message': None,
        'data': {}
    }
    return res


class YzModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            res = super().list(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '', 'data': res.data})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': '查询失败', 'data': {}})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'errCode': 0, 'errMessage': '', 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        return Response({'errCode': 0, 'errMessage': '', 'data': {}})

    def destroy(self, request, *args, **kwargs):
        res = super().destroy(request, *args, **kwargs)
        return Response({'errCode': 0, 'errMessage': '删除成功', 'data': {}})

    def create(self, request, *args, **kwargs):
        request.data['service_provider'] = request.user.company.id
        super().create(request, *args, **kwargs)
        return Response({'errCode': 0, 'errMessage': '新增成功', 'data': {}})


class FalseDeleteModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            res = super().list(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '', 'data': res.data})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': '查询失败', 'data': e}, 200)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'errCode': 0, 'errMessage': '', 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        try:
            request.data['service_provider'] = request.user.company.id
            super().update(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': str(e), 'data': {}}, 200)

    def destroy(self, request, *args, **kwargs, ):
        try:
            self.get_queryset().filter(id=kwargs['pk']).update(if_deleted=True)
            return Response({'errCode': 0, 'errMessage': '删除成功', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': '删除失败', 'data': {}})

    def create(self, request, *args, **kwargs):
        try:
            request.data['service_provider'] = request.user.company.id
            super().create(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '新增成功', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': str(e), 'data': {}})


class IntegratedPlatformFalseDeleteModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            res = super().list(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '请求成功', 'data': res.data})
        except Exception as e:
            print(e)
            return Response({'errCode': 1, 'errMessage': '查询失败', 'data': {}})

    def retrieve(self, request, *args, **kwargs):
        """
        获取某一个对象的具体信息,一般访问的url都为/obj/id/这种新式,get_object()可以获取到这个id的对象
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'errCode': 0, 'errMessage': '', 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '更新成功', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': str(e), 'data': {}}, 200)

    def destroy(self, request, *args, **kwargs):
        try:
            self.get_queryset().filter(id=kwargs['pk']).update(if_deleted=True)
            return Response({'errCode': 0, 'errMessage': '删除成功', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 1, 'errMessage': '删除失败', 'data': {}})

    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
            return Response({'errCode': 0, 'errMessage': '新增成功', 'data': {}})
        except Exception as e:
            print(e)
            return Response({'errCode': 500, 'errMessage': str(e), 'data': {}})
