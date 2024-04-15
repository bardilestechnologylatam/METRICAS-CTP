from datetime import datetime, timedelta
import urllib.parse
import json

def get_last_hits():
    today = datetime.today()
    yesterday_2 = today - timedelta(days=1)
    init_yesterday_2 = yesterday_2.replace(hour=0, minute=0, second=0, microsecond=0)
    end_yesterday_2 = yesterday_2.replace(hour=23, minute=59, second=59, microsecond=999999)
    init_yestedaday2_str = init_yesterday_2.strftime('%Y-%m-%d %H:%M:%S.000')
    end_yestedaday2_str = end_yesterday_2.strftime('%Y-%m-%d %H:%M:%S.000')
    query_filter = {"startTimestamp": init_yestedaday2_str, "endTimestamp": end_yestedaday2_str}
    query_filter_encoded = urllib.parse.quote(str(query_filter))
    url_base = "em/usage?"
    url_params = f"queryFilter={query_filter_encoded}&_=1710444066974"
    url = url_base + url_params
    return url

def get_hits_peer_dates(start_time, end_time):
    # Convertir las cadenas de startTime y endTime a objetos datetime
    start_date = datetime.strptime(start_time, '%Y-%m-%d')
    end_date = datetime.strptime(end_time, '%Y-%m-%d')
    # Agregar un día más al objeto fecha_fin_dia_anterior
    end_date += timedelta(days=1)
    # Definir el formato de las fechas de inicio y fin
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S.000')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S.000')
    # Construir el filtro de consulta
    query_filter = {"startTimestamp": start_date_str, "endTimestamp": end_date_str}
    query_filter_encoded = urllib.parse.quote(str(query_filter))
    # Construir la URL
    url_base = "em/usage?"
    url_params = f"queryFilter={query_filter_encoded}&_=1710444066974"
    url = url_base + url_params
    return url

def get_virtualization(data):
    try:
        json_data = get_json_data(data)
    except InvalidDataException as e:
        print("Error:", e)
        return []

    folder_ommit = ["traffic_templates", "recorded_traffic", ".settings"]
    result = []

    try:
        for folder in json_data.get("virtualAssetsProject", {}).get("folders", []):
            if folder["name"] not in folder_ommit:
                tribu = folder["name"]
                result.extend(process_folder(folder, tribu))
    except Exception as e:
        print("Error:", e)

    return result


def get_json_data(data):
    if not data or not isinstance(data[0], dict):
        raise InvalidDataException("Invalid data format")
    return data[0]


def process_folder(folder, tribu):
    result = []

    if folder.get("virtualAssets"):
        result.extend(process_virtual_assets(folder["virtualAssets"], tribu, "Na", "Na"))

    if folder.get("folders"):
        for clan in folder["folders"]:
            result.extend(process_clan(clan, tribu))

    return result


def process_clan(clan, tribu):
    result = []
    clan_name = clan.get("name")

    if clan.get("folders"):
        for celula in clan["folders"]:
            result.extend(process_celula(celula, tribu, clan_name))

    return result


def process_celula(celula, tribu, clan_name):
    result = []
    celula_name = celula.get("name")

    if celula.get("virtualAssets"):
        result.extend(process_virtual_assets(celula["virtualAssets"], tribu, clan_name, celula_name))

    return result


def process_virtual_assets(virtual_assets, tribu, clan_name, celula_name):
    result = []
    for virt in virtual_assets:
        virt_id = virt.get("id")
        virt_name = virt.get("name")
        result.append({"virt_name": virt_name, "virt_id": virt_id, "tribu": tribu, "clan": clan_name, "celula": celula_name})
    return result


class InvalidDataException(Exception):
    pass



# def get_virtualization(data):
#     json_data = data[0]
#     data=[]
#     folder_ommit = ["traffic_templates", "recorded_traffic", ".settings"]
#     for folder in json_data["virtualAssetsProject"]["folders"]:
#         if folder["name"] not in folder_ommit:
#             tribu = folder["name"]
#             if folder["virtualAssets"]!= None:
#                 for virt in folder["virtualAssets"]:
#                     virt_id = virt["id"]
#                     virt_name = virt["name"]
#                     data.append({"virt_name":virt_name, "virt_id":virt_id, "tribu": tribu, "clan": "Na", "celula": "Na"})
#             if folder["folders"] != None:
#                 for clanes in folder["folders"]:
#                     clan_name = clanes["name"]
#                     #print(clanes, type(clanes))
#                     if clanes["folders"]!= None:
#                         #print(clan_name, "tiene celulas")
#                         for celulas in clanes["folders"]:
#                             celula_name = celulas["name"]
#                             if celulas["virtualAssets"]!= None:
#                                #print(celula_name, " Tiene virtualizaciones")
#                                 for virt in celulas["virtualAssets"]:
#                                     virt_id = virt["id"]
#                                     virt_name = virt["name"]
#                                     data.append({"virt_name":virt_name, "virt_id":virt_id, "tribu":tribu, "clan": clan_name, "celula": celula_name})


#     return data