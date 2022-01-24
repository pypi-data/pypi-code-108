from . import markov, shapley, heuristicos

class Modelo():
    """
    Crear un objeto con los datos a partir del cual calcular los distintos modelos.
    
    :param data: Data con la cual crear los modelos, formateada o no.
    :type data: dataframe or list
    
    :param formateada: Si la data tiene una columna de recorridos y otra con la conversion.
    :type formateada: bool
    """
    def __init__(self, data, formateada=True):
        self.data = data
        self.formateada = formateada

        return None

    def markov(self, orden=1, ventana=30, touchpoints=8, conversion=True):
        """
        Si no esta formateada, lo hace. Luego, crea un modelo de Markov en base a los parametros.

        :param orden: El orden del modelo de Markov, entre 1 y 4.
        :type orden: int

        :param ventana: La cantidad de dias que se toman antes de cada conversion.
        :type ventana: int

        :param touchpoints: La cantidad de canales maxima que se toma por cada conversion.
        :type touchpoints: int

        :param conversion: Si se corta el camino con cada nueva conversion.
        :type conversion: bool
        """
        # formatear la data
        if self.formateada == False:
            parametros = {
                'orden' : orden,
                'ventana' : ventana,
                'touchpoints' : touchpoints,
                'conversion' : conversion
            }
            data = markov.formatear(self.data, parametros)
        else:
            data = self.data

        # calcular el modelo de markov
        resultado = markov.calcular(data)

        return resultado

    def shapley(self, ventana=30, touchpoints=8):
        """
        Si no esta formateada, lo hace. Luego, crea un modelo de Shapley en base a los parametros.

        :param ventana: La cantidad de dias que se toman antes de cada conversion.
        :type ventana: int

        :param touchpoints: La cantidad de canales maxima que se toma por cada conversion.
        :type touchpoints: int
        """
        # formatear la data
        if self.formateada == False:
            parametros = {
                'ventana' : ventana,
                'touchpoints' : touchpoints,
            }
            data = shapley.formatear(self.data, parametros)        
        else:
            data = self.data

        # calcular el modelo de shapley
        resultado = shapley.calcular(data.values.tolist())

        return resultado

    def heuristicos(self, ventana=30, touchpoints=8):
        """
        Si no esta formateada, lo hace. Luego, crea un modelo last click.

        :param ventana: La cantidad de dias que se toman antes de cada conversion.
        :type ventana: int

        :param touchpoints: La cantidad de canales maxima que se toma por cada conversion.
        :type touchpoints: int
        """
        # formatear la data
        if self.formateada == False:
            parametros = {
                'ventana' : ventana,
                'touchpoints' : touchpoints,
            }
            data = shapley.formatear(self.data, parametros)        
        else:
            data = self.data

        # calcular los modelos heuristicos
        resultado = heuristicos.calcular(data)

        return resultado

    def comparacion(self):
        pass


