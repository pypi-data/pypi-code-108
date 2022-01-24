# refer to the following for more info
# "https"://maps.alk.com/PCMDoc/Reports
# "https"://maps.alk.com/PCMDoc/CalcMilesReport

class PcMilerConfig():

    url = "https://pcmiler.alk.com/apis/rest/v1.0/Service.svc/route/routeReports"
    query_params = {
      "stops": None, # must be provided at query time
      "reports": "CalcMiles",
      "vehType": "Truck",
      "routeType": "Shortest",
      "hwyOnly": "true",
      "custRdSpeeds": "false",
      "avoidFavors": "false",
      "afSetIDs": "",
      "overrideClass": "FiftyThreeFoot",
      "distUnits": "Miles",
      "fuelUnits": "Gallons",
      "avoidTolls": "true",
      "inclFerryDist": "true",
      "openBorders": "true",
      "restrOverrides": "false",
      "hazMat": "",
      "routeOpt": "DestinationFixed",
      "lang": "ENUS",
      "hubRouting": "false",
      "vehDimUnits": "English",
      "vehHeight": "13'6\"",
      "vehLength": "53'",
      "vehWidth": "96\"",
      "vehWeight": "14000",
      "axles": "8",
      "truckConfig": "none",
      "LCV": "false",
      "inclTollData": "true",
      "fuelEconLoad": "8.5",
      "fuelEconEmpty": "11.9",
      "costPerFuelUnit": "13",
      "costGHG": "5.2",
      "costMaintLoad": "12.2",
      "costMaintEmpty": "8.9",
      "costTimeLoad": "15.5",
      "costTimeEmpty": "12.6",
      "exchangeRate": "1.01",
      "tollPlan": "ezpass",
      "region": "NA",
      "dataVersion": "current",
      "authToken": None
    }
