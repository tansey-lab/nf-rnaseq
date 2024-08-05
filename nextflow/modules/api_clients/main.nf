process HGNC {
    conda "${params.condaEnv}"

    input:
    val(inputId)

    output:
    path("${inputId}_hgnc.tsv"), emit: geneName

    script:
    """
    get_gene_name \\
        -i ${inputId} \\
        -d HGNC \\
        -c ${params.requestsCache} \\
        -t \\
        > ${inputId}_hgnc.tsv
    """
}

process UNIPROT {
    conda "${params.condaEnv}"

    input:
    val(inputId)

    output:
    path("${inputId}_uniprot.tsv"), emit: geneName

    script:
    """
    get_gene_name \\
        -i ${inputId} \\
        -d UniProt \\
        -c ${params.cacheDir} \\
        -t \\
        > ${inputId}_uniprot.tsv
    """
}

process BIOMART {
    conda "${params.condaEnv}"

    input:
    val(inputIds)

    output:
    path("*_biomart.tsv"), emit: geneName

    script:
    def uuid = UUID.randomUUID().toString()
    """
    get_gene_name \\
        -i "${inputIds}" \\
        -d BioMart \\
        -c ${params.requestsCache} \\
        -t \\
        > ${uuid}_biomart.tsv
    """
}

process CONCAT_TSV {
    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    path(tsvFiles)

    output:
    path("gene_name_concat.tsv")

    script:
    """
    grep -h . ${tsvFiles} > gene_name_concat.tsv
    """
}
