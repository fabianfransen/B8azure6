from Bio import Entrez, Medline
import re
import httplib2 as http
import json

def main():
    zoekwoord = "((variant [tiab] OR variants [tiab] OR mutation [tiab] OR mutations [tiab] OR substitutions [tiab] OR substitution [tiab] )AND (""loss of function"" [tiab] OR ""loss-of-function"" [tiab] OR ""haplo-insufficiency"" [tiab] OR haploinsufficiency [tiab]OR ""bi-allelic"" [tiab] OR ""biallelic"" [tiab] OR recessive [tiab] OR homozygous [tiab] OR heterozygous [tiab] OR ""de novo""[tiab] OR dominant [tiab] OR ""X-linked"" [tiab]) AND (""intellectual"" [tiab] OR ""mental retardation"" [tiab] OR ""cognitive""[tiab] OR ""developmental"" [tiab] OR ""neurodevelopmental"" [tiab]) AND “last 2 years”[dp] AND KDM3B)"
    count = search_count(zoekwoord)
    id_list = search_artikel(zoekwoord, count)
    hgnc_genen, dict_genpanels = genpanel()
    resultaat = gegevens(id_list, hgnc_genen, dict_genpanels)
    print(resultaat)


def search_count(zoekwoord):
    Entrez.email = "Your.Name.Here@example.org"
    handle = Entrez.esearch(db="nucleotide", term=zoekwoord, idtype="acc")
    record = Entrez.read(handle)

    count = int(record['Count'])

    return count


def search_artikel(zoekwoord, count):
    handle = Entrez.esearch(db="pubmed", term=zoekwoord, retmax=count)
    record = Entrez.read(handle)

    id_list = record['IdList']

    return id_list


def gegevens(id_list, hgnc_genen, dict_genpanels):
    resultaat = []
    for i in range(len(id_list)):
        handle = Entrez.efetch(db="pubmed", id=id_list[i], rettype="medline")
        records = Medline.parse(handle)
        for record in records:
            resultaatperhit = []
            gen = ""
            resultaatperhit.append(record['PMID'])
            resultaatperhit.append(record['TI'])
            datum_nieuw = dag(str(record['DP']))
            datum_compleet = datum(datum_nieuw)
            resultaatperhit.append(datum_compleet)
            datum_nieuw = datum_maken(str(record['LR']))
            datum_compleet = datum(datum_nieuw)
            resultaatperhit.append(datum_compleet)
            abstract = record['AB']
            gevonden_genen, abstract = genen_genpanel(abstract, hgnc_genen)
            gevonden_genen = genen(gevonden_genen, abstract)
            gevonden_genpanels = aanwezige_genpanels(gevonden_genen, dict_genpanels)
            hgnc_gevonden_genen = gen_namen(gevonden_genen)
            for item in hgnc_gevonden_genen:
                gen = gen + item + " "
            resultaatperhit.append(gen)
            resultaatperhit.append(gevonden_genpanels)
            resultaat.append(resultaatperhit)

    return resultaat


def genpanel():
    hgnc_genen = []
    bestand = open("GenPanels_merged_DG-2.17.0.txt", 'r')
    dict_genpanels = {}
    bestand.readline()
    for line in bestand:
        line = line.split("\t")
        hgnc_genen.append(line[0])
        dict = {line[0]: line[1]}
        dict_genpanels.update(dict)
    bestand.close()

    return hgnc_genen, dict_genpanels


def genen_genpanel(abstract, hgnc_genen):
    gevonden_genen = []
    abstract = re.sub("BACKGROUND", "background", abstract)
    abstract = re.sub("METHODS", "methods", abstract)
    abstract = re.sub("CONCLUSIONS", "conclusions", abstract)
    abstract_ = re.sub("RESULTS", "results", abstract)

    for item_ in hgnc_genen:
        match = re.findall("{}".format(item_), abstract_)
        if len(match) > 0:
            gevonden_genen.append(match[0])

    return gevonden_genen, abstract_


def genen(gevonden_genen, abstract):
    genen_tussenstap = []
    match = re.findall("[A-Z][A-Z].....", abstract)
    for result in match:
        genen_tussenstap.append(result)

    for item in genen_tussenstap:
        match = re.search("[0-9]+", item)
        if match is not None:
            item = item.split(",")
            item = item[0].split(" ")
            if item[0] not in gevonden_genen:
                gevonden_genen.append(item[0])

    return gevonden_genen


def gen_namen(gevonden_genen):
    try:
        from urlparse import urlparse
    except ImportError:
        from urllib.parse import urlparse
    hgnc_gevonden_genen = []
    headers = {'Accept': 'application/json'}
    for name in gevonden_genen:
        uri = 'http://rest.genenames.org/search/'
        path = name
        target = urlparse(uri + path)
        method = 'GET'
        body = ''
        h = http.Http()
        response, content = h.request(target.geturl(), method, body, headers)
        if response['status'] == '200':
            data = json.loads(content)
            print('Symbol:' + data['response']['docs'][0]['symbol'])
            hgnc_gevonden_genen.append(data['response']['docs'][0]['symbol'])
        else:
            print('Error detected: ' + response['status'])
    return hgnc_gevonden_genen


def datum_maken(datum_):
    datum_nieuw = ""
    count = 0
    string = ""
    for cijfer in datum_:
        string = string + cijfer
        count += 1
        if count == 4:
            datum_nieuw = datum_nieuw + string
            string = ""
        if count == 6:
            datum_nieuw = datum_nieuw + " " + string
            string = ""
        if count == 8:
            datum_nieuw = datum_nieuw + " " + string

    return datum_nieuw


def dag(date):
    dicht_dagen = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08", "9": "09"}
    dagen = date.split(" ")
    dag_ = dicht_dagen.get(dagen[2])
    datum_nieuw = dagen[0] + " " + dagen[1] + " " + dag_

    return datum_nieuw


def datum(date):
    dict_maanden = {"01": "Jan", "02": "Feb", "03": "Mrt", "04": "Apr", "05": "Mei", "06": "Jun", "07": "Jul",
                    "08": "Aug", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Dec"}
    datum_ = date.split(" ")
    maand = dict_maanden.get(datum_[1])

    if maand is None:
        datum_compleet = datum_[2] + "-" + datum_[1] + "-" + datum_[0]
    else:
        datum_compleet = datum_[2] + "-" + maand + "-" + datum_[0]

    return datum_compleet


def aanwezige_genpanels(gevonden_genen, dict_genpanels):
    gevonden_genpanels = ""
    for gen in gevonden_genen:
        if dict_genpanels.get(gen) is not None:
            gevonden_genpanels = gevonden_genpanels + dict_genpanels.get(gen) + "\n"

    gevonden_genpanels = gevonden_genpanels.replace("\n", "")
    return gevonden_genpanels


main()
