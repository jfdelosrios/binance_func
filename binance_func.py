# -*- coding: utf-8 -*-
"""varios_2.py"""

from C_Simbolo import C_Simbolo
from binance.client import Client,  BinanceRequestException, BinanceAPIException
from binance.exceptions import BinanceAPIException


def cantMonedas(client:Client, moneda: str) -> float:
    """cantidad de monedas de una cierta moneda."""

    for i in client.get_account()['balances']:
        if(i['asset'] != moneda):
            continue

        return float(i['free'])

    return -1


def cantMonedas_1(cuenta:dict, moneda: str) -> dict:
    """cantidad de monedas de una cierta moneda en una cierta cuenta."""
 
    client = Client(
            api_key = cuenta['api_key'], 
            api_secret = cuenta['secret_key']
        )

    try:

        client = client.get_account()

    except BinanceAPIException as error:
        
        return {
                'status': ['error', 'Binance, {}'.format(error)], 
                'out': -1
            }

    for i in client['balances']:
        if(i['asset'] != moneda):
            continue

        return {'status': ['ok', ''], 'out': float(i['free'])}

    return {
            'status': ['error', 'Binance, No encontré la moneda {}'.format(moneda)], 
            'out': -1
        }
        

def cancelarOrdenesPendientes(cuenta:dict, simbolo:str) -> bool:
    """
    Intenta cancelar todas las ordenes pendientes de un simbolo. Donde:
        * client es el cliente de binance (ver 
          https://python-binance.readthedocs.io/en/latest/binance.html#module-binance.client ).
        * simbolo, es el simbolo de las pendientes que se desean cerrar.
    """
 
    client = Client(
            api_key = cuenta['api_key'], 
            api_secret = cuenta['secret_key']
        )

    orders = client.get_open_orders(symbol = simbolo)

    for i in orders:

        result = client.cancel_order(
                symbol = simbolo, 
                orderId = i['orderId']
            )
        
    return True
        

def abrirInstantanea(
        cuenta:dict, 
        simbolo: str, 
        cantidadTotal:float,
        inversion:float, # viene de 0 a 100
        riesgoPorcentual:float
    ) -> dict:
    """
    Intenta meter una orden instantanea a mercado.

    inversion:float, Nos dice cuanto porcentaje (de 0 a 100) van a ser usados de la cantidadTotal

    riesgoPorcentual: 1 / Abs(OpenPrice - stopLoss)

    """
 
    client = Client(
            api_key = cuenta['api_key'], 
            api_secret = cuenta['secret_key']
        )

    obj_simbolo = C_Simbolo(simbolo = simbolo)

    usd = cantidadTotal * inversion / 100.0

    cant_monedas = usd * riesgoPorcentual

    dict_cant = obj_simbolo.formatear_cant_monedas(cant_monedas)
    
    if(dict_cant['status'][0] == 'error'):

        return {
            'status': [
                       'error',
                       'error, {}. {}, cant_monedas {}.'.format(
                            dict_cant['status'][1],
                            obj_simbolo.Name(),
                            dict_cant['out']
                            )
                    ]
                }

    try:

        order = client.order_market_buy(
                symbol = simbolo,
                quantity  = dict_cant['out']
            )
        
    except BinanceRequestException as error:
        return {'status': ['error',error]}
    except BinanceAPIException as error:
        return {'status': ['error',error]}

    return  {
            'status':   [
                            'ok',
                            'Compra de {} {} satisfactoria.'.format(
                                        dict_cant['out'], 
                                        simbolo
                                    )
                        ]
        }


def cerrarPosicion(cuenta:dict, obj_simbolo:C_Simbolo) -> dict:
    """Intenta cerrar posicion."""

    dict_cant = cantMonedas_1(cuenta, obj_simbolo.get_monedaBase())

    if(dict_cant['status'][0] == 'error'):
        return dict_cant
    
    dict_cant = obj_simbolo.formatear_cant_monedas(dict_cant['out'])
    
    if((dict_cant['status'][0] == 'error')):

        return {
            'status': [
                       'error',
                       'error, {}. {}, cant_monedas {}.'.format(
                            dict_cant['status'][1],
                            obj_simbolo.Name(),
                            dict_cant['out']
                            )
                    ]
                }

    if(dict_cant['out'] == 0):
            
        return  {
                'status': [
                        'ok', 
                        'No encontre posicion abierta para {}.'.format(
                                obj_simbolo.Name()
                            )
                    ]
            }

    client = Client(
            api_key = cuenta['api_key'], 
            api_secret = cuenta['secret_key']
        )

    try:
        order = client.order_market_sell(
                symbol = obj_simbolo.Name(),
                quantity = dict_cant['out']
            )
        
    except BinanceRequestException as error:
        return {
            'status': [
                        'error', 
                        'Error con cierre de {}. {}'.format(
                            obj_simbolo.Name(), 
                            str(error)
                            )
                        ]
                }

    except BinanceAPIException as error:
        return {
            'status': [
                        'error', 
                        'Error con cierre de {}. {}'.format(
                            obj_simbolo.Name(), 
                            str(error)
                            )
                        ]
                }
    
    return  {
            'status': ['ok', 'Posicion {} cerrada.'.format(obj_simbolo.Name())]
        }


def ponerOrdenPendiente(
        cuenta:dict, 
        simbolo:str, 
        precioApertura:float, 
        cant_monedas:float
    ) -> dict:
    """Intenta poner una orden pendiente."""
 
    client = Client(
            api_key = cuenta['api_key'], 
            api_secret = cuenta['secret_key']
        )

    obj_simbolo = C_Simbolo(simbolo = simbolo)

    dict_precio = obj_simbolo.formatear_precio(
            precioApertura
        )
    
    if(dict_precio['status'][0] == 'error'):

        return {
            'status': [
                       'error',             
                       'error, {}. {}, precio {}.'.format(
                            dict_precio['status'][1],
                            obj_simbolo.Name(),
                            dict_precio['out']
                            )
                       ]
                }

    dict_precio['out'] = '{:.8f}'.format(dict_precio['out'])

    dict_cant = obj_simbolo.formatear_cant_monedas(cant_monedas)
    
    if(dict_cant['status'][0] == 'error'):

        return {
            'status': [
                       'error',
                       'error, {}. {}, cant_monedas {}, precio {}.'.format(
                            dict_cant['status'][1],
                            obj_simbolo.Name(), 
                            dict_cant['out'], 
                            dict_precio['out']
                            )
                    ]
                }

    try:

        order = client.order_limit_buy(
            symbol = obj_simbolo.Name(),
            quantity = dict_cant['out'],
            price = str(dict_precio['out'])
            )
        
    except BinanceAPIException as error:

        return {
            'status': [
                       'error',
                       'error, {}. {}, cant_monedas {}, precio {}.'.format(
                            error,
                            obj_simbolo.Name(), 
                            dict_cant['out'], 
                            dict_precio['out']
                            )
                    ]
                }

    return {
        'status': [
                    'ok',
                    "Orden {} puesta por {} {} en {} {}, ".format( 
                        order['type'],       
                        order['origQty'],
                        obj_simbolo.Simbol_info()['baseAsset'], 
                        order['price'],
                        obj_simbolo.Simbol_info()['quoteAsset']
                        )
                ]
            }
