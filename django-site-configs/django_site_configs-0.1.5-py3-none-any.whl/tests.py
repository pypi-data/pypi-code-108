from django.test import Client, TestCase
from django.urls import reverse
from core.config import ExampleClass
from .models import SiteConfigModel

class ExampleTests(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_default_value(self):
        default = ExampleClass().get_key_value()
        self.assertEquals(default, {"example": "Default Value"})

    def test_create_config(self):
        self.assertEqual(SiteConfigModel.objects.count(), 0)
        uri = reverse("core-example")
        response = self.client.post(uri, {"example": "Testing"})
        self.assertEqual(SiteConfigModel.objects.count(), 1)
        config = SiteConfigModel.objects.last()
        self.assertEqual(config.key, "core.config.ExampleClass")
        self.assertEqual(config.value, {"example": "Testing"})
        self.assertEqual(config.value, ExampleClass().get_key_value())
        self.assertEqual(config.value["example"], ExampleClass().get_key_value("example"))

    def test_save(self):
        example = ExampleClass()
        self.assertEqual(example.instance, None)
        example.save("new value", "test key")
        setting = SiteConfigModel.objects.last()
        self.assertEqual(example.instance, setting)
        self.assertEqual(example.value, setting.value)
        self.assertEqual(example.value, {"test key": "new value"})

    def test_save_via_dict(self):
        example = ExampleClass()
        test_data = {"hello": "world", "test": "value"}
        example.save(test_data)
        self.assertEqual(example.value, test_data)
        self.assertEqual(example.get_key_value("hello"), "world")
        self.assertEqual(example.get_key_value("test"), "value")

    def test_delete(self):
        ExampleClass().save("Testing", "example")
        self.assertEqual(SiteConfigModel.objects.count(), 1)
        ExampleClass().delete()
        self.assertEqual(ExampleClass().instance, None)
        self.assertEqual(ExampleClass().value, dict())
        self.assertEqual(SiteConfigModel.objects.count(), 0)
