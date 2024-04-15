import os
import sys

from datetime import datetime, timedelta

from controller.mongo_manager import MongoDBManager
from controller.HTTPRequest import HTTPRequest
from controller.Hits import  get_virtualization, get_hits_peer_dates
from pymongo.errors import PyMongoError
from flask import Flask, jsonify, request, make_response
from flask_wtf import CSRFProtect 

app = Flask(__name__)
csrf = CSRFProtect(app)


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

BASE_URL_CTP = os.environ.get('BASE_URL_CTP')
CRONJOB_CONDITION = os.environ.get('CRONJOB')


def get_hit_virts(start_time, end_time):
    requester = HTTPRequest(BASE_URL_CTP)
    data_hits = requester.get_json(endpoint=get_hits_peer_dates(start_time,end_time))
    data_virt_list = requester.get_json(endpoint="em/virtualizeservers/virtualassets")
    data_virts = get_virtualization(data_virt_list)
    # Iterar sobre los elementos de data_hits["items"]
    for item in data_hits["items"]:
        # Obtener el resourceId del elemento actual
        virt_name_hits = item.get("name")
        acum = 0
        for virt_data in data_virts:
            virt_name_asset =  virt_data["virt_name"]

            tribu =  virt_data["tribu"]
            celula =  virt_data["celula"]
            clan =  virt_data["clan"]

            if virt_name_hits == virt_name_asset:
                item.update({
                    "tribu": tribu ,
                    "celula": celula ,
                    "clan": clan
                })
                acum+=1
        
        
        if acum==0:
            # Si no se encuentra ninguna coincidencia, establecer los valores como "Na"
            item.update({
                "tribu": "Deprecado",
                "celula": "Deprecado",
                "clan": "Deprecado",
            })
    data_hits['date_init_filter'] = start_time
    data_hits['date_end_filter'] = end_time
    return data_hits

def save_last_hits():
    manager = MongoDBManager()
    # Obtener la fecha y hora actual en formato datetime
    today = datetime.now()
    # Restar dos días a la fecha actual
    yesterday_2 = today - timedelta(days=1)
    fecha_formateada = yesterday_2.strftime("%Y-%m-%d")
    
    virt_data_hits = get_hit_virts(fecha_formateada, fecha_formateada)
    # # Convertir la fecha resultante a formato ISODate
    date_iso = yesterday_2.isoformat()
    virt_data_hits['date_query'] = date_iso
    try:
        manager = MongoDBManager()
        manager.insertar_documento(virt_data_hits)
    except BaseException as bs:
        if isinstance(bs, SystemExit):
            raise  # Re-lanzar la excepción SystemExit
        return {"Error": str(bs)}
    
    return True


@app.route('/save', methods=['GET'])
def save_last_hits_api():
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    if start_time is None or end_time is None:
        datos_param = {
            "error": "Parámetros no válidos"
        }
        response = jsonify(datos_param)
        response.status_code = 404
        return response
    
    else:
        try:
            manager = MongoDBManager()
            manager.insertar_documento(get_hit_virts(start_time, end_time))
        except PyMongoError as e:
            return {"Error de MongoDB": str(e)}
        except Exception as e:
            return {"Error": str(e)}



@app.route('/', methods=['GET'])
@csrf.exempt
def obtener_datos():
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    if start_time is None or end_time is None:
        datos_param = {
            "error": "Parametros no valido"
        }
        response = jsonify(datos_param)
        response.status_code = 404
        return response
    
    else:
        return get_hit_virts(start_time, end_time)
    

        
if __name__ == "__main__":
    if CRONJOB_CONDITION == "true":
        save_last_hits()
    else:
        print("Servidor puerto 5000")
        app.run(host='0.0.0.0', port=5000)