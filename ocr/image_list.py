import os
import csv
import json
import rdflib
import requests
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF, SKOS, OWL, Namespace, NamespaceManager, XSD

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDG = Namespace("http://purl.bdrc.io/graph/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
MBBT = Namespace("http://mbingenheimer.net/tools/bibls/")
CBCT_URI = "https://dazangthings.nz/cbc/text/"
CBCT = Namespace(CBCT_URI)

NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)
NSM.bind("", BDO)
NSM.bind("bdg", BDG)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdf", RDF)
NSM.bind("cbct", CBCT)
NSM.bind("mbbt", MBBT)

def get_id_for_str(id):
	pass

def getTerm(jsonNode):
	type = jsonNode["type"]
	if type == "uri":
		return URIRef(jsonNode["value"])
	if type == "literal":
		dt = URIRef(jsonNode["datatype"]) if "datatype" in jsonNode else XSD.string
		lt = jsonNode["xml:lang"] if "xml:lang" in jsonNode else None
		return Literal(jsonNode["value"], datatype=dt, lang=lt)


def get_volumes_for_work(workId):
	"""
	returns a list of volume info in ascending volume order. Volume info should be a class I think.
	"""
	qname = NSM.qname(workId)
	# asumption is made that there is no more than 400 volumes
	r = requests.get('http://purl.bdrc.io/query/table/volumesForWork?R_RES=%s&format=json&pageSize=400' % qname)
	if r.status_code != 200:
		print("error %d when fetching volumes for %s" %(r.status_code, qname))
		return
	# the result of the query is already in ascending volume order
	res = []
	rres = r.json()
	for b in rres["results"]["bindings"]:
		res.append({"volnum": getTerm(b["volnum"]), "volumeId": getTerm(b["volid"])})
	return res

def get_simple_imagelist_for_vol(volumeId):
	qname = NSM.qname(volumeId)
	# asumption is made that there is no more than 400 volumes
	r = requests.get('https://iiifpres.bdrc.io/il/v:%s' % qname)
	if r.status_code != 200:
		print("error "+r.status_code+" when fetching volumes for "+qname)
		return
	return r.json()

def get_iiif_service_for_filename(volumeId, filename):
	qname = NSM.qname(volumeId)
	return "https://iiif.bdrc.io/%s::%s" % (qname, filename)

def get_iiif_canvas_for_filename(volumeId, filename):
	qname = NSM.qname(volumeId)
	return "https://iiifpres.bdrc.io/v:%s/canvas/%s" % (qname, filename)

def get_iiif_fullimg_for_filename(volumeId, filename):
	qname = NSM.qname(volumeId)
	filenameext = filename[-4:].lower()
	ext = "jpg"
	if filenameext == ".tif" or filenameext == "tiff":
		ext = "png"
	return "https://iiif.bdrc.io/%s::%s/full/max/0/default.%s" % (qname, filename, ext)

def shorten(id):
	return id[29:]

# getting volumes for W4CZ5369, W23703, W1KG13126, W1GS66030 and W22704
outdir = "tsv/"
if not os.path.exists(outdir):
    os.makedirs(outdir)
worksIds = [
	URIRef("http://purl.bdrc.io/resource/W4CZ5369"),
	URIRef("http://purl.bdrc.io/resource/W23703"),
	URIRef("http://purl.bdrc.io/resource/W1KG13126"),
	URIRef("http://purl.bdrc.io/resource/W1GS66030"),
	URIRef("http://purl.bdrc.io/resource/W22704")
]
for workId in worksIds:
	volseqnum = 0
	csvfile = open('tsv/%s-1.tsv' % (shorten(workId)), 'w', newline='')
	csvwriter = csv.writer(csvfile, delimiter='\t',quoting=csv.QUOTE_MINIMAL)
	csvwriter.writerow(["volumeId", "imgSeq", "imgUrl"])
	for volinfo in get_volumes_for_work(workId):
		volseqnum += 1
		volnum = int(volinfo["volnum"])
		if volseqnum >= 10:
			volseqnum = 1
			csvfile.close()
			csvfile = open('tsv/%s-%d.tsv' % (shorten(workId), volnum), 'w', newline='')
			csvwriter = csv.writer(csvfile, delimiter='\t',quoting=csv.QUOTE_MINIMAL)
			csvwriter.writerow(["volumeId", "imgSeq", "imgUrl"])
		imgseq = 0
		volumeId = volinfo["volumeId"]
		for imginfo in get_simple_imagelist_for_vol(volumeId):
			imgseq += 1
			if imgseq < 3:
				continue
			csvwriter.writerow([shorten(volumeId), imgseq, get_iiif_fullimg_for_filename(volumeId, imginfo["filename"])])
	csvfile.close()