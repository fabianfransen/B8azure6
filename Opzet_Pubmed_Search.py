from Bio import Entrez


def main():
    zoekwoord = "((variant [tiab] OR variants [tiab] OR mutation [tiab] OR mutations [tiab] OR substitutions [tiab] OR substitution [tiab] )AND (""loss of function"" [tiab] OR ""loss-of-function"" [tiab] OR ""haplo-insufficiency"" [tiab] OR haploinsufficiency [tiab]OR ""bi-allelic"" [tiab] OR ""biallelic"" [tiab] OR recessive [tiab] OR homozygous [tiab] OR heterozygous [tiab] OR ""de novo""[tiab] OR dominant [tiab] OR ""X-linked"" [tiab]) AND (""intellectual"" [tiab] OR ""mental retardation"" [tiab] OR ""cognitive""[tiab] OR ""developmental"" [tiab] OR ""neurodevelopmental"" [tiab]) AND “last 2 years”[dp] AND KDM3B)"
    count = search_count(zoekwoord)
    id_list = search_artikel(zoekwoord, count)
    resultaat = gegevens(id_list, count)


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
    resultaat = [[] for _ in range(kolom)]
    count = 0
    for i in range(len(id_list)):
        handle = Entrez.efetch(db="pubmed", id=id_list[i], retmode="xml")
        records = Entrez.read(handle)
        for record in records["PubmedArticle"]:
            if count <= kolom:
                line = str(record["MedlineCitation"]["PMID"]).split("'")
                resultaat[count].append(str(line[0]))
                count += 1
                resultaat[count].append(record["MedlineCitation"]["Article"]["ArticleTitle"])
                count += 1
                line2 = str(record["MedlineCitation"]["DateCompleted"]).split(",")
                jaar = line2[0], line2[1], line2[2]
                jaar = str(jaar).replace("'", "").replace("{", "").replace("}", "").replace("(", "").replace(")", "")
                resultaat[count].append(jaar)
                count += 1

    return resultaat


main()
