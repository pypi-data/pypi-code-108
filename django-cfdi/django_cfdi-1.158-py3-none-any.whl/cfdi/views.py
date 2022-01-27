from django.shortcuts import render
from django.contrib import messages
from .models import Cfdi

def editar_cfdi(request, xml_string, *, error=None, title="Editar XML antes de timbrar"):
    """
    Permite editar un CFDI no timbrado
    """

    return render(request,
        'cfdi/editar_cfdi.html', 
        {
            'xml_string':xml_string,
            'title': title,
            'error':error,
        }
    )


