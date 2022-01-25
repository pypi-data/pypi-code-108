import json
import pathlib
from pathlib import Path
from datamodel_code_generator import InputFileType, generate

base_path = pathlib.Path(__file__).parent.parent
schema_path = base_path.joinpath("schemas/openlabel-1-0-0-edited.json")

with open(schema_path) as fp:
    json_schema = json.load(fp)
    output = Path(base_path / 'models/models.py')
    generate(
        str(json_schema),
        input_file_type=InputFileType.JsonSchema,
        reuse_model=True,
        output=output,
        use_schema_description=True,
        class_name='OpenLabelAnnotation'
    )
    model: str = output.read_text()
    print(model)
print(f"Model generated to: {output}")
