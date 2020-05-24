from flask import Flask, render_template, request, send_file
from Bio import Entrez, Medline
import re

app = Flask(__name__)


@app.route('/')
def hello_world():
    zoekwoord = ""
    teruggave = ""
    return render_template('page.html', zoekwoord=zoekwoord, teruggave=teruggave)


@app.route('/', methods=['GET', 'POST'])
def page():
    # searchword = request.form["myTextarea"]
    year = request.form["year"]
    gene = request.form["gene"]
    # print(searchword)
    print(gene)
    print(year)
    zoekwoord = request.form["myTextarea"]
    print(zoekwoord)
    count = search_count(zoekwoord)
    id_list = search_artikel(zoekwoord, count, year)
    hgnc_genen = genpanel()
    resultaat = gegevens(id_list, hgnc_genen)
    print(resultaat)
    teruggave = ("   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                 + "   <tr>\n"
                 + "   <th onclick=\"sortTable(0)\"><p1>ID</p1></th>\n"
                 + "   <th onclick=\"sortTable(1)\"><p1>Title</p1></th>\n"
                 + "   <th onclick=\"sortTable(2)\"><p1>Date</p1></th>\n"
                 + "   <th onclick=\"sortTable(3)\"><p1>Gene</p1></th>\n"
                 + "   </tr>")
    for a in resultaat:
        teruggave = teruggave + "<tr>"
        teruggave = teruggave + "<td>" \
                                  "<a href = \"https://pubmed.ncbi.nlm.nih.gov/" + str(a[0]) + "\">" \
                                  "" + str(a[0]) + "</a></td>"
        teruggave = teruggave + "<td><p2>" + str(a[1]) + "</p2></td>"
        teruggave = teruggave + "<td><p2>" + str(a[2]) + "</p2></td>"
        teruggave = teruggave + "<td><p2>" + str(a[3]) + "</p2></td>"
        teruggave = teruggave + "</tr>"

    return render_template("page.html", zoekwoord=zoekwoord, teruggave=teruggave, year=year, gene=gene)


def search_count(zoekwoord):
    Entrez.email = "Your.Name.Here@example.org"
    handle = Entrez.esearch(db="nucleotide", term=zoekwoord, idtype="acc")
    record = Entrez.read(handle)

    count = int(record['Count'])

    return count


def search_artikel(zoekwoord, count, year):
    handle = Entrez.esearch(db="pubmed", term=zoekwoord, retmax=count, mindate=year)
    record = Entrez.read(handle)

    id_list = record['IdList']

    return id_list


def gegevens(id_list, hgnc_genen):
    resultaat = []
    for i in range(len(id_list)):
        handle = Entrez.efetch(db="pubmed", id=id_list[i], rettype="medline")
        records = Medline.parse(handle)
        for record in records:
            resultaatperhit = []
            gen = ""
            resultaatperhit.append(record['PMID'])
            resultaatperhit.append(record['TI'])
            resultaatperhit.append(record['DP'])
            abstract = record['AB']
            gevonden_genen, abstract = genen_genpanel(abstract, hgnc_genen)
            gevonden_genen = genen(gevonden_genen, abstract)
            for item in gevonden_genen:
                gen = gen + item + " "
            resultaatperhit.append(gen)
            resultaat.append(resultaatperhit)

    return resultaat


def genpanel():
    hgnc_genen = []
    bestand = open("GenPanels_merged_DG-2.17.0.txt", 'r')
    bestand.readline()
    for line in bestand:
        hgnc_genen.append(line.split("\t")[0])
    bestand.close()

    return hgnc_genen


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

@app.route('/download')
def download_file():
    p = "output.png"
    return send_file(p)