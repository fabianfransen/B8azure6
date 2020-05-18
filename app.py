from flask import Flask, render_template, request
from Bio import Entrez

app = Flask(__name__)


@app.route('/')
def hello_world():
    zoekwoord = ""
    teruggave = ("   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                 + "   <tr>\n"
                 + "   <th onclick=\"sortTable(0)\"><p1>ID</p1></th>\n"
                 + "   <th onclick=\"sortTable(1)\"><p1>Title</p1></th>\n"
                 + "   <th onclick=\"sortTable(2)\"><p1>Date</p1></th>\n"
                 + "   </tr>")
    return render_template('page.html', zoekwoord=zoekwoord, teruggave=teruggave)


@app.route('/', methods=['GET', 'POST'])
def page():
    searchword = request.form["myTextarea"]

    print(searchword)

    zoekwoord = request.form["myTextarea"]
    count = search_count(zoekwoord)
    id_list = search_artikel(zoekwoord, count)
    resultaat = gegevens(id_list, count)
    print(resultaat)
    teruggave = ("   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                 + "   <tr>\n"
                 + "   <th onclick=\"sortTable(0)\"><p1>ID</p1></th>\n"
                 + "   <th onclick=\"sortTable(1)\"><p1>Title</p1></th>\n"
                 + "   <th onclick=\"sortTable(2)\"><p1>Date</p1></th>\n"
                 + "   </tr>")
    for a in resultaat:
        teruggave = teruggave + "<tr>"
        teruggave = teruggave + "<td><p2>" + str(a[0]) + "</p2></td>"
        teruggave = teruggave + "<td><p2>" + str(a[1]) + "</p2></td>"
        teruggave = teruggave + "<td><p2>" + str(a[2]) + "</p2></td>"
        teruggave = teruggave + "</tr>"

    return render_template("page.html", zoekwoord=zoekwoord, teruggave=teruggave)


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


def gegevens(id_list, count):
    kolom = count * 3

    resultaat = []
    count = 0
    for i in range(len(id_list)):
        handle = Entrez.efetch(db="pubmed", id=id_list[i], retmode="xml")
        records = Entrez.read(handle)
        for record in records["PubmedArticle"]:
            if count <= kolom:
                resultaatperhit = []
                line = str(record["MedlineCitation"]["PMID"]).split("'")
                resultaatperhit.append(str(line[0]))
                count += 1
                resultaatperhit.append(record["MedlineCitation"]["Article"]["ArticleTitle"])
                count += 1
                line2 = str(record["MedlineCitation"]["DateCompleted"]).split(",")
                print(line2)
                jaar = line2[0], line2[1], line2[2]
                print(jaar)
                jaar = str(jaar).replace("'", "").replace("{", "").replace("}", "").replace("(", "").replace(")", "")
                print(jaar)
                resultaatperhit.append(jaar)
                count += 1
                resultaat.append(resultaatperhit)

    return resultaat


if __name__ == '__main__':
    app.run()
