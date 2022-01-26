from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attr import define, field

from infima_client.core.models.mbs.cohort_story import MbsCohortStory
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1CohortSummary")


@define(auto_attribs=True)
class CohortV1CohortSummary:
    """
    Attributes:
        average_aols (Union[Unset, float]):
        average_fico (Union[Unset, float]):
        average_ls (Union[Unset, float]):
        average_ltv (Union[Unset, float]):
        average_refi (Union[Unset, float]):
        average_security_factor (Union[Unset, float]):
        average_wac (Union[Unset, float]):
        average_wala (Union[Unset, float]):
        average_wam (Union[Unset, float]):
        coupon (Union[Unset, float]):
        iss_upb (Union[Unset, float]):
        name (Union[Unset, str]):
        num_loans (Union[Unset, int]):
        num_pools (Union[Unset, int]):
        story (Union[Unset, MbsCohortStory]):  Default: MbsCohortStory.NULL_COHORT_STORY.
        ticker (Union[Unset, str]):
        upb (Union[Unset, float]):
        vintage (Union[Unset, int]):
    """

    average_aols: Union[Unset, float] = UNSET
    average_fico: Union[Unset, float] = UNSET
    average_ls: Union[Unset, float] = UNSET
    average_ltv: Union[Unset, float] = UNSET
    average_refi: Union[Unset, float] = UNSET
    average_security_factor: Union[Unset, float] = UNSET
    average_wac: Union[Unset, float] = UNSET
    average_wala: Union[Unset, float] = UNSET
    average_wam: Union[Unset, float] = UNSET
    coupon: Union[Unset, float] = UNSET
    iss_upb: Union[Unset, float] = UNSET
    name: Union[Unset, str] = UNSET
    num_loans: Union[Unset, int] = UNSET
    num_pools: Union[Unset, int] = UNSET
    story: Union[Unset, MbsCohortStory] = MbsCohortStory.NULL_COHORT_STORY
    ticker: Union[Unset, str] = UNSET
    upb: Union[Unset, float] = UNSET
    vintage: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        average_aols = self.average_aols
        average_fico = self.average_fico
        average_ls = self.average_ls
        average_ltv = self.average_ltv
        average_refi = self.average_refi
        average_security_factor = self.average_security_factor
        average_wac = self.average_wac
        average_wala = self.average_wala
        average_wam = self.average_wam
        coupon = self.coupon
        iss_upb = self.iss_upb
        name = self.name
        num_loans = self.num_loans
        num_pools = self.num_pools
        story: Union[Unset, str] = UNSET
        if not isinstance(self.story, Unset):
            story = self.story.value

        ticker = self.ticker
        upb = self.upb
        vintage = self.vintage

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if average_aols is not UNSET:
            field_dict["averageAols"] = average_aols
        if average_fico is not UNSET:
            field_dict["averageFico"] = average_fico
        if average_ls is not UNSET:
            field_dict["averageLs"] = average_ls
        if average_ltv is not UNSET:
            field_dict["averageLtv"] = average_ltv
        if average_refi is not UNSET:
            field_dict["averageRefi"] = average_refi
        if average_security_factor is not UNSET:
            field_dict["averageSecurityFactor"] = average_security_factor
        if average_wac is not UNSET:
            field_dict["averageWac"] = average_wac
        if average_wala is not UNSET:
            field_dict["averageWala"] = average_wala
        if average_wam is not UNSET:
            field_dict["averageWam"] = average_wam
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if iss_upb is not UNSET:
            field_dict["issUpb"] = iss_upb
        if name is not UNSET:
            field_dict["name"] = name
        if num_loans is not UNSET:
            field_dict["numLoans"] = num_loans
        if num_pools is not UNSET:
            field_dict["numPools"] = num_pools
        if story is not UNSET:
            field_dict["story"] = story
        if ticker is not UNSET:
            field_dict["ticker"] = ticker
        if upb is not UNSET:
            field_dict["upb"] = upb
        if vintage is not UNSET:
            field_dict["vintage"] = vintage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        average_aols = d.pop("averageAols", UNSET)

        average_fico = d.pop("averageFico", UNSET)

        average_ls = d.pop("averageLs", UNSET)

        average_ltv = d.pop("averageLtv", UNSET)

        average_refi = d.pop("averageRefi", UNSET)

        average_security_factor = d.pop("averageSecurityFactor", UNSET)

        average_wac = d.pop("averageWac", UNSET)

        average_wala = d.pop("averageWala", UNSET)

        average_wam = d.pop("averageWam", UNSET)

        coupon = d.pop("coupon", UNSET)

        iss_upb = d.pop("issUpb", UNSET)

        name = d.pop("name", UNSET)

        num_loans = d.pop("numLoans", UNSET)

        num_pools = d.pop("numPools", UNSET)

        _story = d.pop("story", UNSET)
        story: Union[Unset, MbsCohortStory]
        if isinstance(_story, Unset):
            story = UNSET
        else:
            story = MbsCohortStory(_story)

        ticker = d.pop("ticker", UNSET)

        upb = d.pop("upb", UNSET)

        vintage = d.pop("vintage", UNSET)

        cohort_v1_cohort_summary = cls(
            average_aols=average_aols,
            average_fico=average_fico,
            average_ls=average_ls,
            average_ltv=average_ltv,
            average_refi=average_refi,
            average_security_factor=average_security_factor,
            average_wac=average_wac,
            average_wala=average_wala,
            average_wam=average_wam,
            coupon=coupon,
            iss_upb=iss_upb,
            name=name,
            num_loans=num_loans,
            num_pools=num_pools,
            story=story,
            ticker=ticker,
            upb=upb,
            vintage=vintage,
        )

        cohort_v1_cohort_summary.additional_properties = d
        return cohort_v1_cohort_summary

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
