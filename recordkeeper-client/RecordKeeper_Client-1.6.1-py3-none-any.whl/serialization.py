import base64
import json
from uuid import UUID
from typing import Dict

from rkclient.entities import Artifact, PEM


class ArtifactSerialization:

    @staticmethod
    def from_json(txt: str) -> Artifact:
        obj = json.loads(txt)
        return ArtifactSerialization.from_dict(obj)

    @staticmethod
    def to_dict(art: Artifact) -> Dict:
        obj = {
            "ID": art.ID.hex,
            "Type": art.Type,
            "Properties": art.Properties,
            "CreatedAt": art.CreatedAt,
            "TaxonomyFiles": None,
        }
        if art.TaxonomyFiles is not None:
            obj["TaxonomyFiles"] = {tkey: _encode_as_base64(tval) for tkey, tval in art.TaxonomyFiles.items()}
        return obj

    @staticmethod
    def from_dict(d: Dict) -> Artifact:
        art = Artifact(
            id=UUID(hex=d['ID']),
            artifact_type=d['Type'],
            properties=d['Properties'],
        )
        art.CreatedAt = d['CreatedAt']
        art.TaxonomyFiles = None
        if d['TaxonomyFiles'] is not None:
            art.TaxonomyFiles = {tkey: _decode_from_base64(tval) for tkey, tval in d['TaxonomyFiles'].items()}
        return art


class PEMSerialization:

    @staticmethod
    def to_json(pem: PEM) -> str:
        pred_id = None
        if pem.Predecessor is not None:
            pred_id = pem.Predecessor.hex
        obj = {
            "ID": pem.ID.hex,
            "Type": pem.Type,
            "Predecessor": pred_id,
            "Emitter": pem.Emitter.hex,
            "TimestampClient": pem.TimestampClient,
            "TimestampReceived": pem.TimestampReceived,
            "Properties": pem.Properties,
            "Version": pem.Version,
            "Tag": pem.Tag,
            "TagNamespace": pem.TagNamespace,
            "UsesArtifacts": [ArtifactSerialization.to_dict(a) for a in pem.UsesArtifacts],
            "ProducesArtifacts": [ArtifactSerialization.to_dict(a) for a in pem.ProducesArtifacts],
        }
        return json.dumps(obj)

    @staticmethod
    def from_json(txt: str) -> PEM:
        obj = json.loads(txt)
        return PEMSerialization.from_dict(obj)

    @staticmethod
    def from_dict(obj: Dict, art_solely_id: bool = False) -> PEM:
        pred = None
        if obj["Predecessor"] is not None:
            pred = UUID(hex=obj["Predecessor"])

        pem = PEM(UUID(hex=obj["ID"]),
                  obj["Type"],
                  pred,
                  UUID(hex=obj["Emitter"]),
                  obj["TimestampClient"])
        pem.Properties = obj["Properties"]
        pem.Tag = obj["Tag"]
        pem.TagNamespace = obj["TagNamespace"]

        if art_solely_id:
            pem.UsesArtifacts = [Artifact(UUID(hex=uid), '', {}, True) for uid in obj["UsesArtifacts"]]
            pem.ProducesArtifacts = [Artifact(UUID(hex=uid), '', {}, True) for uid in obj["ProducesArtifacts"]]
        else:
            pem.UsesArtifacts = [ArtifactSerialization.from_dict(a) for a in obj["UsesArtifacts"]]
            pem.ProducesArtifacts = [ArtifactSerialization.from_dict(a) for a in obj["ProducesArtifacts"]]
        return pem


def _encode_as_base64(content: str) -> str:
    content_bytes = content.encode()
    content_base64_bytes = base64.b64encode(content_bytes)
    content_base64 = content_base64_bytes.decode()
    return content_base64


def _decode_from_base64(content_base64: str) -> str:
    content_base64_bytes = content_base64.encode()
    content_bytes = base64.b64decode(content_base64_bytes)
    content = content_bytes.decode()
    return content
