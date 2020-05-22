from Bio import Entrez, Medline
import re


def main():
    zoekwoord = "((variant [tiab] OR variants [tiab] OR mutation [tiab] OR mutations [tiab] OR substitutions [tiab] OR substitution [tiab] )AND (""loss of function"" [tiab] OR ""loss-of-function"" [tiab] OR ""haplo-insufficiency"" [tiab] OR haploinsufficiency [tiab]OR ""bi-allelic"" [tiab] OR ""biallelic"" [tiab] OR recessive [tiab] OR homozygous [tiab] OR heterozygous [tiab] OR ""de novo""[tiab] OR dominant [tiab] OR ""X-linked"" [tiab]) AND (""intellectual"" [tiab] OR ""mental retardation"" [tiab] OR ""cognitive""[tiab] OR ""developmental"" [tiab] OR ""neurodevelopmental"" [tiab]) AND “last 2 years”[dp] AND KDM3B)"
    count = search_count(zoekwoord)
    id_list = search_artikel(zoekwoord, count)
    hgnc_genen = genpanel()
    resultaat = gegevens(id_list, hgnc_genen)


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


main()
