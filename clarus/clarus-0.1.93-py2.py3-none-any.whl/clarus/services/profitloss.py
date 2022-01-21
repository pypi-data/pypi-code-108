import clarus.services

def explain(output=None, **params):
    return clarus.services.api_request('ProfitLoss', 'Explain', output=output, **params)

def hypothetical(output=None, **params):
    return clarus.services.api_request('ProfitLoss', 'Hypothetical', output=output, **params)

def predict(output=None, **params):
    return clarus.services.api_request('ProfitLoss', 'Predict', output=output, **params)

