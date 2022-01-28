import unittest

from brevettiai.interfaces import vue_schema_utils as vue


class TestSchema(unittest.TestCase):

    def test_build_schema(self):
        ns_training = "training."
        ns_data = "data."

        s = vue.SchemaBuilder()
        s.add_field(vue.label("Data"))
        s.add_field(
            vue.number_input("Image height", model=ns_data + "image_height", default=224, min=0, max=4096, step=1))
        s.add_field(
            vue.number_input("Image width", model=ns_data + "image_width", default=224, min=0, max=4096, step=1))
        s.add_field(vue.field_class_mapping(model=ns_data+"class_mapping"), fast={"test":["A"], "test2":["B"]})
        s.add_field(vue.field_classes(default=["test", "test2", "test3"]))
        s.add_field(vue.label("Training"))
        s.add_field(vue.number_input("Epochs", model=ns_training + "epochs", default=10, min=1, max=1000, step=1),
                    slow=100, fast=10)
        s.add_field(vue.number_input("Batch size", model=ns_training + "batch_size", default=8, min=1, max=64, step=1),
                    aggressive=1)

        schema = s.schema

        assert isinstance(schema, dict)
        assert "fields" in schema
        assert "presets" in schema
        assert isinstance(schema["fields"], (list, tuple))
        assert all(x in schema["presets"] for x in ["fast", "slow", "aggressive"])
        assert schema["presets"]["fast"]["data"]["class_mapping"] == '{"test": ["A"], "test2": ["B"]}'
        assert schema["presets"]["fast"]["training"]["epochs"] == 10

        with self.assertRaises(ValueError, msg="Test set preset on non-existing field"):
            s.add_preset("test", "this.is.not.a.field", 120)

        vue.SchemaBuilder.from_schema(schema).schema


if __name__ == '__main__':
    unittest.main()
