
import requests, json


def cambiarMoneda(from_currency, to_currency, value) : 
  


    url = 'https://api.exchangerate-api.com/v4/latest/USD'

    response = requests.get(url) 
    data = response.json()

    fromDolar = value / data['rates'][from_currency]
    convertido = fromDolar * data['rates'][to_currency]
    return int(convertido)
  
  
def obtenerMonedas() : 
    url = 'https://api.exchangerate-api.com/v4/latest/USD'

    response = requests.get(url) 
    data = response.json()

    return data['rates']


def cambiarMonedaJson(from_currency, to_currency, value, data):
    fromDolar = value / data[from_currency]
    convertido = fromDolar * data[to_currency]
    return int(convertido)

# Driver code 
if __name__ == "__main__" :
    # currency code 
    from_currency = "USD"
    to_currency = "COP"

    data = obtenerMonedas()
    # function calling 
    print(cambiarMonedaJson('COP', 'MXN', 2000000, data))