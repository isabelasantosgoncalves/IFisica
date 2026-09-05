from datetime import date, datetime

def texto_ou_nulo(valor):
    if valor is None:
        return None

    valor = str(valor).strip()

    return valor or None


def data_br(valor):
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")

    return valor


def formatar_datas(registro, *campos):
    for campo in campos:
        if campo in registro:
            registro[campo] = data_br(registro[campo])

    return registro
