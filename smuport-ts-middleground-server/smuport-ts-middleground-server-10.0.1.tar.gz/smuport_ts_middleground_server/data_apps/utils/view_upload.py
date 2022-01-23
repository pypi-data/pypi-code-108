# from data_apps.ent_plan.models import Cargo, DeliveryTypePic, ContainerNo
from django.db import transaction
# from wms_serve import settings
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
import xlrd as xlrd

from data_apps.tlms_wms_public_table.models import Cargo
from data_middle_platform_serve import settings


class UploadView(APIView):
    """
        上传视图
        """
    parser_classes = (MultiPartParser, FileUploadParser)

    def post(self, request):
        upload_file = request.data['filename']
        base_dir = settings.MEDIA_ROOT
        storage = base_dir + '/cargo/images/'
        # 系统当前时间，拼接到文件名后
        now_time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        name_list = upload_file.name.split('.')
        file_name = name_list[0] + '-' + now_time + '.' + name_list[1]
        new_file = storage + file_name
        with open(new_file, 'wb+') as destination:
            for chunk in upload_file.chunks():
                destination.write(chunk)
            destination.close()
        response = 'media/cargo/images/' + file_name
        return Response({'errCode': 0, 'errMessage': '上传成功', 'data': response})


class DeleteCargoImageView(APIView):
    """
    删除货物图片接口
    """

    def delete(self, request, pk):
        filtered_data = Cargo.objects.filter(id=pk).first()
        print(filtered_data)
        filtered_data.image_path = ""
        filtered_data.save()
        return Response({'errCode': 0, 'errMessage': '删除成功', 'data': {}})


# class UploadDeliveryCtnView(APIView):
#     """
#         上传拆箱方式照片视图
#         """
#     parser_classes = (MultiPartParser, FileUploadParser)
#
#     def post(self, request):
#         pic = DeliveryTypePic()
#         ctn_id = request.data['ctn_id']
#         pic.ctn = ContainerNo.objects.get(id=ctn_id)
#         upload_file = request.data['filename']
#         file_obj = request.FILES.get('filename')
#         pic.image_path = file_obj
#         pic.save()
#         base_dir = settings.MEDIA_ROOT
#         # # 系统当前时间，拼接到文件名后
#         now_time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
#         name_list = file_obj.name.split('.')
#         file_name = name_list[0] + '-' + now_time + '.' + name_list[1]
#         file_name2 = file_name.replace('"', '')
#         response = base_dir + "\\" + file_name2
#         return Response({'errCode': 0, 'errMessage': '上传成功', 'data': response})


class CargoExcelUploadView(APIView):
    """
    货物excel上传
    """
    parser_classes = (MultiPartParser, FileUploadParser)

    def post(self, request):
        if request.method == 'POST':
            # f = request.FILES.get('file')
            upload_file = request.data['filename']
            excel_type = upload_file.name.split('.')[1]
            if excel_type in ['xlsx', 'xls']:
                # 开始解析上传的excel表格
                wb = xlrd.open_workbook(filename=None, file_contents=upload_file.read())
                table = wb.sheets()[0]
                rows = table.nrows  # 总行数
                try:
                    with transaction.atomic():  # 控制数据库事务交易
                        for i in range(1, rows):
                            rowVlaues = table.row_values(i)
                            if rowVlaues[14] == '是':
                                automatic_license = True
                            else:
                                automatic_license = False
                            Cargo.objects.create(code=int(rowVlaues[0]), name_en=rowVlaues[1], name=rowVlaues[2], hs_code=rowVlaues[3],
                                                 declare_elements=rowVlaues[4], gb_code=rowVlaues[5], duty_rate=rowVlaues[6],
                                                 specs_quantity=rowVlaues[7], specs_unit=rowVlaues[8], pack_quantity=rowVlaues[9],
                                                 pack_unit=rowVlaues[10], source_area=rowVlaues[11], standard_name=rowVlaues[12],
                                                 common_name=rowVlaues[13], if_automatic_license=automatic_license, brand=rowVlaues[15])
                        return Response({'errCode': 0, 'errMessage': '文件导入成功', 'data': {}})
                except:
                    return Response({'errCode': 1, 'errMessage': '解析excel文件或者数据插入错误', 'data': {}})
            else:
                return Response({'errCode': 1, 'errMessage': '文件格式不支持，请上传xls、xlsx格式文件', 'data': {}})
