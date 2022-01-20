#!/usr/bin/env python
import hanlp
from flask import Flask, request, jsonify
from typing import Optional, List, Dict, Tuple
import codefast as cf

# Restrict to a particular path.
_HANLP = hanlp.load(
    hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)

app = Flask(__name__)


@app.route('/hanlp', methods=['POST', 'GET'])
def hanlp_parse():
    texts = request.json.get('texts')
    resp = _HANLP(texts)
    cf.info('hanlp result', resp)
    return jsonify(resp)
