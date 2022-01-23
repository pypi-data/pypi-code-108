from oarepo_model_builder.builders import OutputBuilder, process
from oarepo_model_builder.stack import ModelBuilderStack


class JSONBaseBuilder(OutputBuilder):
    output_file_name: str = None
    output_file_type: str = None
    parent_module_root_name: str = None

    def model_element_enter(self, stack: ModelBuilderStack):
        top = stack.top
        data = top.data
        data = self.call_components('model_element_enter', data, stack=stack)
        match stack.top_type:
            case stack.PRIMITIVE:
                self.output.primitive(top.key, data)
            case stack.LIST:
                self.output.enter(top.key, [])
            case stack.DICT:
                self.output.enter(top.key, {})

    def model_element_leave(self, stack: ModelBuilderStack):
        self.call_components('model_element_leave', stack.top.data, stack=stack)
        if stack.top_type != stack.PRIMITIVE:
            self.output.leave()

    @process('/model')
    def enter_model(self, stack: ModelBuilderStack):
        output_name = self.settings[self.output_file_name]
        self.output = self.builder.get_output(self.output_file_type, output_name)
        self.on_enter_model(output_name, stack)

    def on_enter_model(self, output_name, stack: ModelBuilderStack):
        pass
