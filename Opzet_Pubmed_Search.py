from Bio import Entrez

Entrez.email = "Your.Name.Here@example.org"
handle = Entrez.esearch(db="nucleotide", term="((variant [tiab] OR variants [tiab] OR mutation [tiab] OR mutations [tiab] OR substitutions [tiab] OR substitution [tiab] )AND (""loss of function"" [tiab] OR ""loss-of-function"" [tiab] OR ""haplo-insufficiency"" [tiab] OR haploinsufficiency [tiab]OR ""bi-allelic"" [tiab] OR ""biallelic"" [tiab] OR recessive [tiab] OR homozygous [tiab] OR heterozygous [tiab] OR ""de novo""[tiab] OR dominant [tiab] OR ""X-linked"" [tiab]) AND (""intellectual"" [tiab] OR ""mental retardation"" [tiab] OR ""cognitive""[tiab] OR ""developmental"" [tiab] OR ""neurodevelopmental"" [tiab]) AND “last 2 years”[dp] AND KDM3B)", idtype="acc")
record = Entrez.read(handle)

count = int(record['Count'])
handle = Entrez.esearch(db="pubmed", term="((variant [tiab] OR variants [tiab] OR mutation [tiab] OR mutations [tiab] OR substitutions [tiab] OR substitution [tiab] )AND (""loss of function"" [tiab] OR ""loss-of-function"" [tiab] OR ""haplo-insufficiency"" [tiab] OR haploinsufficiency [tiab]OR ""bi-allelic"" [tiab] OR ""biallelic"" [tiab] OR recessive [tiab] OR homozygous [tiab] OR heterozygous [tiab] OR ""de novo""[tiab] OR dominant [tiab] OR ""X-linked"" [tiab]) AND (""intellectual"" [tiab] OR ""mental retardation"" [tiab] OR ""cognitive""[tiab] OR ""developmental"" [tiab] OR ""neurodevelopmental"" [tiab]) AND “last 2 years”[dp] AND KDM3B)" , retmax=count)
record = Entrez.read(handle)

id_list = record['IdList']
post_xml = Entrez.epost("pubmed", id=",".join(id_list))
search_results = Entrez.read(post_xml)

webenv = search_results["WebEnv"]
query_key = search_results["QueryKey"]

fetch_handle = Entrez.efetch(db="pubmed", webenv=webenv, query_key=query_key)
data = fetch_handle.read()
fetch_handle.close()
file = open("test_results.txt", 'w')
file.write(data)
file.close()




