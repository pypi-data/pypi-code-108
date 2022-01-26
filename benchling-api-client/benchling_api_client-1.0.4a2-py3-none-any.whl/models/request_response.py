from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assay_result import AssayResult
from ..models.request_response_samples_item import RequestResponseSamplesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestResponse")


@attr.s(auto_attribs=True, repr=False)
class RequestResponse:
    """  """

    _results: Union[Unset, List[AssayResult]] = UNSET
    _samples: Union[Unset, List[RequestResponseSamplesItem]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("results={}".format(repr(self._results)))
        fields.append("samples={}".format(repr(self._samples)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        results: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._results, Unset):
            results = []
            for results_item_data in self._results:
                results_item = results_item_data.to_dict()

                results.append(results_item)

        samples: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._samples, Unset):
            samples = []
            for samples_item_data in self._samples:
                samples_item = samples_item_data.to_dict()

                samples.append(samples_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if results is not UNSET:
            field_dict["results"] = results
        if samples is not UNSET:
            field_dict["samples"] = samples

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_results() -> Union[Unset, List[AssayResult]]:
            results = []
            _results = d.pop("results")
            for results_item_data in _results or []:
                results_item = AssayResult.from_dict(results_item_data)

                results.append(results_item)

            return results

        results = get_results() if "results" in d else cast(Union[Unset, List[AssayResult]], UNSET)

        def get_samples() -> Union[Unset, List[RequestResponseSamplesItem]]:
            samples = []
            _samples = d.pop("samples")
            for samples_item_data in _samples or []:
                samples_item = RequestResponseSamplesItem.from_dict(samples_item_data)

                samples.append(samples_item)

            return samples

        samples = (
            get_samples() if "samples" in d else cast(Union[Unset, List[RequestResponseSamplesItem]], UNSET)
        )

        request_response = cls(
            results=results,
            samples=samples,
        )

        request_response.additional_properties = d
        return request_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def results(self) -> List[AssayResult]:
        if isinstance(self._results, Unset):
            raise NotPresentError(self, "results")
        return self._results

    @results.setter
    def results(self, value: List[AssayResult]) -> None:
        self._results = value

    @results.deleter
    def results(self) -> None:
        self._results = UNSET

    @property
    def samples(self) -> List[RequestResponseSamplesItem]:
        """ Array of samples produced by the request. """
        if isinstance(self._samples, Unset):
            raise NotPresentError(self, "samples")
        return self._samples

    @samples.setter
    def samples(self, value: List[RequestResponseSamplesItem]) -> None:
        self._samples = value

    @samples.deleter
    def samples(self) -> None:
        self._samples = UNSET
