import warnings
from datetime import timezone

import numpy as np
import pandas as pd
from dateutil.tz import gettz

from .api import api_get, api_string_to_datetime
from .helpers import list_to_string, timestep_start

utc = timezone.utc


class SupplyPoint:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.sub_type = data["subType"]
        self.type = data["type"]
        self.__unit_ids = data["unitIds"]
        self.__applied_price_components = None
        self.__price_data = None

    def get_price_components(self):
        if self.__applied_price_components is None:
            self.__load_price_components()
        return self.__applied_price_components

    def __load_price_components(self):
        resp = api_get(
            "supplypoints/pricecomponents", out="json", payload={"ids": str(self.id)}
        )
        self.__applied_price_components = []
        for pc_i in resp[f"{self.id}"]:
            self.__applied_price_components.append(AppliedPriceComponent(pc_i))
        self.__price_data = PriceDataCollection(self.__applied_price_components)

    def get_all_price_component_ids(self):
        return [pc_i.price_component.id for pc_i in self.get_price_components()]

    def load_price_data(self, start_time, end_time):
        url_postfix = "pricecomponents/prices"
        payload = {
            "ids": list_to_string(self.get_all_price_component_ids()).replace(" ", ""),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "timestamp_type": "iso_8601",
        }
        res = api_get(url_postfix, out="json", payload=payload)
        self.__price_data.load_data(res, start=start_time, end=end_time)

    def clear_price_data(self):
        return self.__price_data.clear_data()

    def get_price_data(self):
        if self.__price_data is None:
            self.get_price_components()
        return (
            self.__price_data.get_data(),
            self.__price_data.price_components_details(),
        )


class PriceDataCollection:
    def __init__(self, applied_price_components):
        self.__applied_price_components = applied_price_components
        self.__data = None

    def load_data(self, price_component_data, start, end):
        tz_out = utc
        start_hour = timestep_start("hour", t=start).astimezone(tz_out)
        end_hour = timestep_start("hour", t=end).astimezone(tz_out)
        df_out = pd.DataFrame(
            index=pd.date_range(start_hour, end_hour, freq="H", tz=tz_out)
        )

        for k_i in price_component_data.keys():
            v_i = int(k_i)
            fill_method = None
            pc_ki = price_component_data[k_i]

            # Structuring price data (either fixed, timeseries, or None) to a unique format
            if (pc_ki["fixedPriceData"] is not None) and (
                len(pc_ki["fixedPriceData"]) > 0
            ):
                pc_i = self.__get_price_component(id=v_i)
                tz_local_i = pc_i.get_timezone()

                df_raw_i = pd.DataFrame(pc_ki["fixedPriceData"])
                positions_i = []
                prices_i = []
                for j in df_raw_i["data"].index:
                    df_j = pd.DataFrame(df_raw_i["data"][j])
                    positions_i.append(df_j["position"])
                    prices_i.append(df_j["price"])
                df_raw_i["position"] = positions_i
                df_raw_i["price"] = prices_i
                if "data" in df_raw_i.keys():
                    df_raw_i.drop(columns=["data"], inplace=True)
                for j in ["validFrom", "validTo"]:
                    df_raw_i[j] = pd.to_datetime(df_raw_i[j])

                df_price_raw_i = None
                for index_ij, row_ij in df_raw_i.iterrows():
                    if row_ij["validTo"] >= start:
                        if row_ij["resolution"] == "PT1H":
                            df_base_ij = pd.DataFrame(
                                index=pd.date_range(
                                    row_ij["validFrom"],
                                    row_ij["validTo"],
                                    freq="H",
                                    closed="left",
                                )
                            )
                            df_base_ij["hour"] = df_base_ij.index.tz_convert(
                                tz_local_i
                            ).hour
                            df_price_ij = pd.DataFrame(
                                {
                                    "hour": row_ij["position"] - 1,
                                    "price": row_ij["price"],
                                }
                            )
                            df_i = df_base_ij.merge(
                                df_price_ij, how="left", left_on="hour", right_on="hour"
                            )
                            df_i.set_index(df_base_ij.index, inplace=True)
                        else:
                            if row_ij["resolution"] == "P1D":
                                freq2use = "D"
                            elif row_ij["resolution"] == "P1M":
                                freq2use = "MS"
                            else:
                                raise Exception(
                                    f"Unsupported time resolution {row_ij['resolution']}"
                                )

                            df_i = pd.DataFrame(
                                index=pd.date_range(
                                    row_ij["validFrom"],
                                    row_ij["validTo"],
                                    freq=freq2use,
                                    closed="left",
                                )
                            )

                            dt_hours = (
                                pd.Timestamp(row_ij["validTo"])
                                - pd.Timestamp(row_ij["validFrom"])
                            ).total_seconds() / 3600
                            fill_method = "ffill"
                            df_i["price"] = row_ij["price"][0] / dt_hours

                        if df_price_raw_i is None:
                            df_price_raw_i = df_i.copy()
                        else:
                            df_price_raw_i = df_price_raw_i.append(df_i.copy())

                df_price_i = df_price_raw_i[["price"]]

            elif (pc_ki["timeSeriesData"] is not None) and (
                len(pc_ki["timeSeriesData"]) > 0
            ):
                df_price_i = pd.DataFrame(pc_ki["timeSeriesData"])
                if len(df_price_i) > 0:
                    df_price_i.set_index(
                        pd.to_datetime(df_price_i["time"], infer_datetime_format=True),
                        inplace=True,
                    )
                    df_price_i.drop(columns=["time"], inplace=True)
                else:
                    df_price_i = None

            else:
                df_price_i = None

            if (df_price_i is not None) and ("price" in df_price_i.keys()):
                df_price_i = df_price_i.reindex(df_out.index, method=fill_method)
                df_out[v_i] = df_price_i["price"]
            else:
                df_out[v_i] = np.nan

        self.__data = df_out

    def clear_data(self):
        self.__data = None

    def get_data(self, application_context=None, unit_component_type=None):
        details = self.price_components_details(
            application_context=application_context,
            unit_component_type=unit_component_type,
        )

        name_dict = {}
        for index, row in details.iterrows():
            name_dict[index] = row["name"]

        return self.__data[name_dict.keys()].rename(mapper=name_dict)

    def price_components_details(
        self, application_context=None, unit_component_type=None
    ):
        df_out = pd.DataFrame(
            {"id": [], "name": [], "description": [], "unit": [], "type": []}
        )
        for apc_i in self.__applied_price_components:
            df_out = df_out.append(
                {
                    "id": int(apc_i.price_component.id),
                    "name": apc_i.price_component.name,
                    "description": apc_i.price_component.description,
                    "unit": apc_i.price_component.unit,
                    "application_context": apc_i.application_context,
                    "billing_context": apc_i.billing_context,
                    "unit_component_type": apc_i.price_component.unit_component_type,
                    "type": apc_i.price_component.type,
                },
                ignore_index=True,
            )

        # Refining results if needed
        if application_context is not None:
            df_out = df_out.loc[df_out["application_context"] == application_context, :]
        if unit_component_type is not None:
            df_out = df_out.loc[df_out["unit_component_type"] == unit_component_type, :]

        return df_out.set_index("id")

    def __get_price_component(self, id=None, name=None, price_type=None):
        if id is not None:
            f_val = lambda x: (x.price_component.id == id)
            criterion_value = ("id", id)
        elif name is not None:
            f_val = lambda x: (x.price_component.name == name)
            criterion_value = ("name", name)
        elif price_type is not None:
            f_val = lambda x: (x.price_component.type == price_type)
            criterion_value = ("type", price_type)
        else:
            raise Exception(
                "One of the following parameters must be provided: id, name"
            )

        for apc_i in self.__applied_price_components:
            if f_val(apc_i):
                return apc_i.price_component

        raise Exception(
            f"Price component not found ({criterion_value[0]}={criterion_value[1]})"
        )

    def compute_price_from_demand(self, demand_data, unit="DKK"):
        warnings.warn(
            "Usage of this function is not recommended as it is still in prototyping stage"
        )
        details = self.price_components_details()


class AppliedPriceComponent:
    def __init__(self, data):
        self.id = data["id"]
        self.supplyPointId = data["supplyPointId"]
        self.price_component = PriceComponent(data["priceComponent"])
        self.contractId = data["contractId"]
        self.created = api_string_to_datetime(data["created"])
        if data.get("validFrom") is None:
            self.validFrom = None
        else:
            self.validFrom = api_string_to_datetime(data["validFrom"])

        if data.get("validTo") is None:
            self.validTo = None
        else:
            self.validTo = api_string_to_datetime(data["validTo"])

        self.billing_context = data["billingContext"]
        self.application_context = data["applicationContext"]


class PriceComponent:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.created = api_string_to_datetime(data["created"])
        if data["type"] is None:
            self.type = None
            self.type_id = None
        else:
            self.type = data["type"]["Name"]
            self.type_id = data["type"]["id"]
        self.unit = data["unit"]
        self.format_type = data["formatType"]
        self.application_type = data["applicationType"]
        self.unit_component_type = data["unitComponentType"]
        self.timezone = data["timezone"]

        if data["priceArea"] is not None:
            self.price_area = PriceArea(data["priceArea"])
        else:
            self.price_area = None
        if data["authority"] is not None:
            self.authority = Authority(data["authority"])
        else:
            self.authority = None

    def get_timezone(self):
        return gettz(self.timezone)


class Authority:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]


class PriceArea:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.supply_type = data["supplyType"]
