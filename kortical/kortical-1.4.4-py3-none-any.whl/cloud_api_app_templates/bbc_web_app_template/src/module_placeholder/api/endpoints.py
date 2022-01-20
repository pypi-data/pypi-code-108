from flask import Response, request, render_template
import logging
import pandas as pd

from module_placeholder.authentication import safe_api_call
from module_placeholder.kortical.predict import run_kortical_prediction

logger = logging.getLogger(__name__)


def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/predict', methods=['post'])
    @safe_api_call
    def bbc_predict():
        input_text = request.json['input_text']
        request_data = {
            'text': [input_text]
        }
        df = pd.DataFrame(request_data)
        df = run_kortical_prediction(df)
        predicted_category = df['predicted_category'][0]

        return Response(predicted_category)
