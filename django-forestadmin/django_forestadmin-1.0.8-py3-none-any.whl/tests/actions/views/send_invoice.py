from django.http import JsonResponse

from django_forest.utils.views.action import ActionView


class SendInvoiceActionView(ActionView):
    def post(self, request, *args, **kwargs):
        params = request.GET.dict()
        body = self.get_body(request.body)
        ids = self.get_ids_from_request(request, self.Model)

        return JsonResponse({'success': 'now live'}, safe=False)
