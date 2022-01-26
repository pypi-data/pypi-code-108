from meili_sdk.models.form import FormInstance, Form
from meili_sdk.resources.base import BaseResource


__all__ = (
    "SDKFormResource",
    "FormResource",
)


class FormResource(BaseResource):
    def get_form(self, uuid):
        return self.get(f"api/forms/{uuid}/", expected_class=Form)

    def update_form(self, form):
        return self.patch(
            f"api/forms/{form.uuid}/",
            data=form,
            expected_class=Form,
        )

    def delete_form(self, forms):
        return self.delete(f"api/forms/{forms.uuid}/")


class SDKFormResource(BaseResource):
    def get_forms(self, object_type: str, object_uuid: str):
        return self.get(
            "sdk/forms/",
            expected_class=Form,
            filters={"object_type": object_type, "uuid": object_uuid},
        )

    def get_form_instance(self, object_type: str, object_uuid: str):
        return self.get(
            "sdk/forms/instances/",
            expected_class=FormInstance,
            filters={"object_type": object_type, "uuid": object_uuid},
        )

    def update_form_instance(
        self, object_type: str, object_uuid: str, form_instance: FormInstance
    ):
        return self.post(
            f"sdk/forms/?object_type={object_type}&uuid={object_uuid}",
            expected_class=FormInstance,
            data=form_instance,
        )
