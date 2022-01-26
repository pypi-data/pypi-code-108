import io
from enum import Enum
from pathlib import Path
from typing import Type

import pandas as pd
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.formatter import FormatterBase, FormatterParameters
from pymultirole_plugins.v1.schema import Document
from starlette.responses import Response


class OutputFormat(str, Enum):
    xlsx = 'xlsx'
    csv = 'csv'


class BELTableParameters(FormatterParameters):
    format: OutputFormat = Field(OutputFormat.xlsx, description="Output format")


class BELTableFormatter(FormatterBase):
    """BELTable formatter.
    """

    def format(self, document: Document, parameters: FormatterParameters) \
            -> Response:
        """Parse the input document and return a formatted response.

        :param document: An annotated document.
        :param options: options of the parser.
        :returns: Response.
        """
        parameters: BELTableParameters = parameters
        try:
            series = []
            relations = [a for a in document.annotations if a.labelName == 'relation']
            for rel in relations:
                props = rel.properties
                props.update(
                    {'PubMedID': document.identifier,
                     'EvidenceSentence': document.text[rel.start:rel.end],
                     'PublicationTitle': document.title,
                     'Journal': document.metadata.get('journal', '')
                     }
                )
                series.append(props)
            df = pd.DataFrame.from_records(series)
            resp: Response = None
            filename = f"file.{parameters.format.value}"
            if document.properties and "fileName" in document.properties:
                filepath = Path(document.properties['fileName'])
                filename = f"{filepath.stem}.{parameters.format.value}"
            if parameters.format == OutputFormat.xlsx:
                bio = io.BytesIO()
                df.to_excel(bio, index=False,
                            columns=['Subject', 'Subject.start', 'Subject.end', 'Subject.text', 'Relation',
                                     'Object', 'Object.start', 'Object.end', 'Object.text', 'Score', 'PubMedID',
                                     'EvidenceSentence',
                                     'PublicationTitle',
                                     'Journal'])
                resp = Response(content=bio.getvalue(),
                                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
            elif parameters.format == OutputFormat.csv:
                sio = io.StringIO()
                df.to_csv(sio, index=False,
                          columns=['Subject', 'Subject.start', 'Subject.end', 'Subject.text', 'Relation',
                                   'Object', 'Object.start', 'Object.end', 'Object.text', 'Score', 'PubMedID',
                                   'EvidenceSentence',
                                   'PublicationTitle',
                                   'Journal'])
                resp = Response(content=sio.getvalue(),
                                media_type="text/csv")
                resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
            return resp
        except BaseException as err:
            raise err

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return BELTableParameters
