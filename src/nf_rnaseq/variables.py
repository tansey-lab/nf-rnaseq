from nf_rnaseq import biomart, hgnc, uniprot

DICT_DATABASES = {
    "BioMart": {
        "GET": {
            "api_object": biomart.BioMart,
            "term_in": "ensembl_transcript_id_version",
            "term_out": "external_gene_name",
            "url_base": 'http://www.ensembl.org/biomart/martservice?query=<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE Query><Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" ><Dataset name = "hsapiens_gene_ensembl" interface = "default" ><Filter name = "<TERM_IN>" value = "<IDS>"/><Attribute name = "<TERM_IN>" /><Attribute name = "<TERM_OUT>" /></Dataset></Query>',
            "headers": None,
        },
    },
    "HGNC": {
        "GET": {
            "api_object": hgnc.HGNC,
            "term_in": "mane_select",
            "term_out": "symbol",
            "url_base": "https://rest.genenames.org/fetch",
            "headers": "{'Accept': 'application/json'}",
        }
    },
    "UniProt": {
        "GET": {
            "api_object": uniprot.UniProt,
            "term_in": "UniProtKB_AC-ID",
            "term_out": "Gene_Name",
            "url_base": "https://rest.uniprot.org/uniprotkb",
            "headers": None,
        },
    },
    "UniProtBULK": {
        "POST": {
            "api_object": uniprot.UniProtPOST,
            "term_in": "UniProtKB_AC-ID",
            "term_out": "Gene_Name",
            "url_base": "https://rest.uniprot.org/idmapping/run",
        },
        "GET": {
            "api_object": uniprot.UniProtGET,
            "term_in": "UniProtKB_AC-ID",
            "term_out": "Gene_Name",
            "url_base": "https://rest.uniprot.org/idmapping/status",
            "headers": None,
        },
    },
}
