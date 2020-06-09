from flask import Flask, render_template, request, send_file
from Bio import Entrez, Medline
import re
import json
import httplib2 as http
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():
    zoekwoord = ""
    teruggave = ""
    # print("helloworld 1")
    return render_template('page.html', zoekwoord=zoekwoord, teruggave=teruggave)


@app.route('/', methods=['GET', 'POST'])
def page():
    # print("helloworld 2")

    # searchword = request.form["myTextarea"]
    startdate = request.form["startdate"]
    enddate = request.form["enddate"]
    gene = request.form["gene"]
    # print(searchword)
    zoekwoord = request.form["myTextarea"]
    count, zoekterm = search_count(zoekwoord, startdate, gene, enddate)
    id_list = search_artikel(zoekterm, count)
    hgnc_genen, dict_genpanels = genpanel()
    resultaat = gegevens(id_list, hgnc_genen, dict_genpanels)

    teruggave = ("   <table id=\"ResultTable\" style=\"width:777px; height: 400px; border-collapse: collapse; "
                 "padding: 10px;\""
                 " class=\"sortable-table\" border=\"1\" border-collapse=\"collapse\">"
                 + "   <thead>\n"
                 + "   <tr>\n"
                 + "   <th style=\"padding: 10px;\"><p1>ID</p1></th>\n"
                 + "   <th style=\"padding: 10px;\"><p1>Title</p1></th>\n"
                 + "   <th style=\"padding: 10px;\" class=\"date-sort\"><p1>Date publication</p1></th>\n"
                 + "   <th style=\"padding: 10px;\" class=\"date-sort\"><p1>Date last revised</p1></th>\n"
                 + "   <th style=\"padding: 10px;\"><p1><b>Gene</b> (genpanel)</p1></th>\n"
                 + "   </tr>"
                 + "   </thead>")
    for a in resultaat:
        teruggave = teruggave + "<tr>"
        teruggave = teruggave + "<td style=\"padding: 10px;\">" \
                                "<a href = \"https://pubmed.ncbi.nlm.nih.gov/" + str(a[0]) + "\" target=\"_blank\">" \
                                                                                             "" + str(
            a[0]) + "</a></td>"
        teruggave = teruggave + "<td style=\"padding: 10px;\"><p2>" + str(a[1]) + "</p2></td>"
        teruggave = teruggave + "<td style=\"padding: 10px;\"><p2>" + str(a[2]) + "</p2></td>"
        teruggave = teruggave + "<td style=\"padding: 10px;\"><p2>" + str(a[3]) + "</p2></td>"
        teruggave = teruggave + "<td style=\"padding: 10px;\"><p2>" + str(a[4]) + "</p2></td>"
        teruggave = teruggave + "</tr>"

    teruggave = teruggave + "</table>"
    teruggave = teruggave + "<tr> <td colspan=4> <hr> <a id=\"downloadLink\" onclick=\"exportToExcel(this)\" style=\"cursor" \
                            ": pointer;\"> Download as excel: <img src=\"../static/images/exelimage.jpeg\" onclick=\"exportToExcel(this)\" " \
                            "title=\"Exporteer naar Excel.\"> </a> <br> " \
                            "<a id=\"downloadLink\" onclick=\"exportToCSV(this)\" style=\"cursor" \
                            ": pointer;\">Download as CSV: <img src=\"../static/images/CSV-icon.png\" onclick=\"exportToCSV(this)\" " \
                            "title=\"Exporteer naar CSV.\" width=\"16\"> </a> </td> </tr>"

    if startdate != "" and enddate != "" and gene != "":
        zoekwoord = zoekwoord + ", start date: " + startdate + ", end date: " + enddate + ", gene: " + gene
    elif startdate == "" and enddate != "" and gene != "":
        zoekwoord = zoekwoord + ", " + enddate + ", gene: " + gene
    elif startdate != "" and enddate == "" and gene != "":
        zoekwoord = zoekwoord + ", start date: " + startdate + ", gene: " + gene
    elif startdate != "" and enddate != "" and gene == "":
        zoekwoord = zoekwoord + ", start date: " + startdate + ", end date: " + enddate

    return render_template("page.html", zoekwoord=zoekwoord, teruggave=teruggave, startdate=startdate,
                           enddate=enddate, gene=gene)


def search_count(zoekwoord, startdate, gene, enddate):
    """ Deze functie genereert een datum wat bij de ingegeven zoekterm hoort en voegt deze datum toe aan de zoekterm.
    Er wordt daarna gegeven over er een gen wordt meegegeven, als dat zo is wordt deze toegevoegd aan de zoekterm.
    Daarna wordt er via esearch met Entrez een search gedaan met de zoekterm om te achterhalen hoeveel artikelen
    matchen.

    :param zoekwoord, het zoekwoord wat ingevuld is door de gebruiker
    :param startdate, de begindatum van de zoekopdracht
    :param enddate, de einddatum van de zoekopdracht
    :param gene, het gen voor de zoekopdracht
    :return count, om bij een zoekopdracht op te geven hoeveel artikelen er resultaten moeten worden gegeven
    :return zoekterm, de zoekterm om later een zoekopdracht uit te voeren
    """
    x = datetime.datetime.now()
    jaar = x.strftime("%Y")
    maand = x.strftime("%m")
    jaar_5 = int(x.strftime("%Y")) - 5
    if startdate == "" and enddate != "":
        zoekterm = zoekwoord + " AND {}:{} [dp]".format(jaar_5, enddate)
    elif enddate == "" and startdate != "":
        zoekterm = zoekwoord + " AND {}:{}/{} [dp]".format(startdate, jaar, maand)
    elif startdate == "" and enddate == "":
        zoekterm = zoekwoord + " AND {}:{} [dp]".format(jaar_5, jaar)
    else:
        zoekterm = zoekwoord + " AND {}:{} [dp]".format(startdate, enddate)
    # print(zoekterm)
    ingevulde_genen = str(gene).split(" ")
    if len(gene) != 0:
        for gen in ingevulde_genen:
            zoekterm = zoekterm + " AND {}".format(gen)
    Entrez.email = "Your.Name.Here@example.org"
    handle = Entrez.esearch(db="pubmed", term=zoekterm, idtype="acc")
    record = Entrez.read(handle)

    count = int(record['Count'])

    return count, zoekterm


def search_artikel(zoekterm, count):
    """ Deze fucntie voert met de meegegeven zoekterm een search uit op Pubmed met het aantal artikelen wat gevonden
    is met de zoekterm. Van alle resultaten wordt er een IDlist meegegeven.

    :param zoekterm, de zoekterm voor de zoekopdracht
    :param count, het aantal gevonden artikelen met de zoekterm
    :return id_list, alle gevonden ID's met de zoekterm
    """
    handle = Entrez.esearch(db="pubmed", term=zoekterm, retmax=count)
    record = Entrez.read(handle)

    id_list = record['IdList']

    return id_list


def gegevens(id_list, hgnc_genen, dict_genpanels):
    """ deze functie pakt van elk gevonden artikel het ID, titel, publicatie datum en schrijft deze om naar een format,
    datum last revised en schrijft deze om naar een format, abstract waarin gezocht wordt naar genen. Al deze gegevens
    worden toegevoegd in een lijst, wat later naar een 2d lijst wordt omgezet.

    :param id_list: lijst met alle gevonden ID's met de zoekterm
    :param hgnc_genen: lijst met alle aanwezige genen in het genpanel
    :param dict_genpanels: dictionary met genen van het genpanel met het bijbehorende genpanel
    :return: resultaat: lijst met resultaat per artikel
    """
    resultaat = []
    for i in range(len(id_list)):
        handle = Entrez.efetch(db="pubmed", id=id_list[i], rettype="medline")
        records = Medline.parse(handle)
        for record in records:
            try:
                print(record)
                resultaatperhit = []
                gen = ""
                resultaatperhit.append(record['PMID'])      # id van het artikel
                resultaatperhit.append(record['TI'])        # titel van het artikel
                datum_nieuw = dag(str(record['DP']))        # date van publicatie van het artikel
                datum_compleet = datum(datum_nieuw)
                resultaatperhit.append(datum_compleet)      # datum in hetzelfde format
                datum_nieuw = datum_maken(str(record['LR']))    # date last revised van het artikel
                datum_compleet = datum(datum_nieuw)
                resultaatperhit.append(datum_compleet)      # datum in hetzelfde format
                abstract = record['AB']     # het abstract van het artikel
                gevonden_genen, abstract = genen_genpanel(abstract, hgnc_genen)
                gevonden_genen = genen(gevonden_genen, abstract)
                hgnc_gevonden_genen = gen_namen(gevonden_genen)
                gevonden_genpanels = aanwezige_genpanels(hgnc_gevonden_genen, dict_genpanels)   # genpanels kijken
                resultaatperhit.append(gevonden_genpanels)
                resultaat.append(resultaatperhit)       # eindresultaat in een lijst
            except KeyError:
                try:
                    datum_nieuw = datum_maken(str(record['LR']))
                except KeyError:
                    try:
                        datum_compleet = datum(datum_nieuw)
                        resultaatperhit.append(datum_compleet)
                        abstract = record['AB']
                        gevonden_genen, abstract = genen_genpanel(abstract, hgnc_genen)
                        gevonden_genen = genen(gevonden_genen, abstract)
                        hgnc_gevonden_genen = gen_namen(gevonden_genen)
                        gevonden_genpanels = aanwezige_genpanels(hgnc_gevonden_genen, dict_genpanels)
                        resultaatperhit.append(gevonden_genpanels)
                        resultaat.append(resultaatperhit)
                    except KeyError:
                        pass
                    except UnboundLocalError:
                        pass
                    except ServerNotFoundError:
                        pass
    return resultaat


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
            try:
                # print('Symbol:' + data['response']['docs'][0]['symbol'])
                hgnc_gevonden_genen.append(data['response']['docs'][0]['symbol'])
            except IndexError:
                 print("Gene removed")
        else:
            print('Error detected: ' + response['status'])
    return hgnc_gevonden_genen


def genpanel():
    """ Deze functie opent het genpanel bestand en leest deze in. De gennamen komen in een lijst en er wordt een
    dictionary gemaakt per gennaam en het bijbehorende genpanel.

    :return: hgnc_genen, een lijst met alle genen van de genpanels
    :return: dict_genpanels, een dictionary met een gennaam en de bijbehorende genpanels
    """
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
    """ Deze functie haalt de hoofdletters van de onderdelen van het abstract eruit en gaat de genen van de genpanels
    zoeken in het abstract van het artikel. Alle gevonden genen worden in een lijst toegevoegd.

    :param abstract: het abstract van het artikel
    :param hgnc_genen: alle gennamen van de genpanels
    :return: gevonden_genen, alle gevonden genen in een artikel
    :return abstract, het aangepaste abstract voor verder gebruik
    """
    gevonden_genen = []
    abstract = re.sub("BACKGROUND", "background", abstract)
    abstract = re.sub("METHODS", "methods", abstract)
    abstract = re.sub("CONCLUSIONS", "conclusions", abstract)
    abstract_ = re.sub("RESULTS", "results", abstract)

    for item_ in hgnc_genen:
        match = re.findall("{}".format(item_), abstract_)   # wordt gekeken of een gen in het artikel bevindt
        if len(match) > 0:
            gevonden_genen.append(match[0])

    return gevonden_genen, abstract_


def genen(gevonden_genen, abstract):
    """ Deze functie zoekt met een regular expression naar eventuele genen in het artikel. Als een stukje van de
    abstract van het artikel voldoet aan 2 regular expressions dan wordt deze toegevoegd aan een lijst.

    :param gevonden_genen: alle gevonden genen van de genpanels
    :param abstract: het abstract van het artikel
    :return: gevonden_genen: lijst met alle gevonden genen in het artikel
    """
    genen_tussenstap = []
    match = re.findall("[A-Z][A-Z].....", abstract)     # gezocht op hoofdletters
    for result in match:
        genen_tussenstap.append(result)

    for item in genen_tussenstap:
        match = re.search("[0-9]+", item)       # gezocht op cijfers
        if match is not None:
            item = item.split(",")
            item = item[0].split(" ")
            if item[0] not in gevonden_genen:
                gevonden_genen.append(item[0])

    return gevonden_genen


def datum_maken(datum_):
    """ Deze functie maakt van de gevonden datum een ander format om het resultaat hetzelfde te maken. Het format waarin
    de datum komt te staan is jaar, maand, dag

    :param datum_: de datum van het artikel
    :return: datum_nieuw, het nieuwe format van de datum
    """
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
    """ Deze functie maakt de datum op de juiste manier, waarbij de dag wordt weergegeven met 2 cijfers.

    :param date: de nieuwe datum
    :return: datum_nieuw, de vernieuwde datum
    """
    try:
        dicht_dagen = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08",
                       "9": "09"}
        dagen = date.split(" ")
        dag_ = dicht_dagen.get(dagen[2])
        if dag_ is None:
            datum_nieuw = dagen[0] + " " + dagen[1] + " " + dagen[2]
        else:
            datum_nieuw = dagen[0] + " " + dagen[1] + " " + dag_
    except IndexError:      # als de datum niet met een dag bestaat
        try:
            datum_nieuw = dagen[0] + " " + dagen[1]
        except IndexError:      # als de datum alleen een jaartal heeft
            datum_nieuw = dagen[0]

    return datum_nieuw


def datum(date):
    """ Deze functie zorgt ervoor dat alle datums in 3-letter vorm staan. Daarna wordt er een streepje toegevoegd
    tussen de dag en maand, en maand en jaartal.

    :param date: de datum van het artikel
    :return: datum_compleet, de uiteindelijke datum van het artikel
    """
    try:
        dict_maanden = {"01": "Jan", "02": "Feb", "03": "Mrt", "04": "Apr", "05": "Mei", "06": "Jun", "07": "Jul",
                        "08": "Aug", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Dec"}
        datum_ = date.split(" ")
        maand = dict_maanden.get(datum_[1])

        if maand is None:
            datum_compleet = datum_[2] + "-" + datum_[1] + "-" + datum_[0]
        else:
            datum_compleet = datum_[2] + "-" + maand + "-" + datum_[0]
    except IndexError:      # als de datum alleen uit jaartal en maand bestaat
        try:
            datum_compleet = datum_[1] + "-" + datum_[0]
        except IndexError:      # als de datum alleen uit jaartal bestaat
            datum_compleet = datum_[0]

    return datum_compleet


def aanwezige_genpanels(gevonden_genen, dict_genpanels):
    """ Deze functie voegt alle gevonden genen in een string aan mekaar met eventueel een gevonden genpanel. Elk gen
    wordt dikgedrukt gemaakt.

    :param gevonden_genen: alle gevonden genen in een artikel
    :param dict_genpanels: dictionary met alle gevonden genpanels
    :return: gevonden_genpanels, alle genen met eventuele genpanels
    """
    gevonden_genpanels = ""
    for gen in gevonden_genen:
        if dict_genpanels.get(gen) is not None:
            gevonden_genpanels = gevonden_genpanels + "<b>" + gen + "</b>" + " (" + dict_genpanels.get(gen) + ")  " \
                                 + "<br>"       # gen met genpanel
        else:
            gevonden_genpanels = gevonden_genpanels + "<b>" + gen + "</b>" + "  " + "<br>"  # gen zonder genpanel
    gevonden_genpanels = gevonden_genpanels.replace("\n", "")

    return gevonden_genpanels
