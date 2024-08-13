process HGNC {
    conda "${params.condaEnv}"

    input:
    val(inputId)

    output:
    path("${inputId}_hgnc.tsv"), emit: geneTSV

    script:
    """
    get_gene_name \\
        -i ${inputId} \\
        -d HGNC \\
        -c "${params.outDir}/requests_cache" \\
        -t \\
        > ${inputId}_hgnc.tsv
    """
}

process UNIPROT {
    conda "${params.condaEnv}"

    input:
    val(inputId)

    output:
    path("${inputId}_uniprot.tsv"), emit: geneTSV

    script:
    """
    get_gene_name \\
        -i ${inputId} \\
        -d UniProt \\
        -c "${params.outDir}/requests_cache" \\
        -t \\
        > ${inputId}_uniprot.tsv
    """
}

process UNIPROT_BULK {
    conda "${params.condaEnv}"

    input:
    val(inputIds)

    output:
    path("*_uniprot.tsv"), emit: geneTSV

    script:
    def uuid = UUID.randomUUID().toString()
    """
    get_gene_name \\
        -i "${inputIds}" \\
        -d UniProtBULK \\
        -c "${params.outDir}/requests_cache" \\
        -t \\
        > ${uuid}_uniprot.tsv
    """
}

process BIOMART {
    conda "${params.condaEnv}"

    input:
    val(inputIds)

    output:
    path("*_biomart.tsv"), emit: geneTSV

    script:
    def uuid = UUID.randomUUID().toString()
    """
    get_gene_name \\
        -i "${inputIds}" \\
        -d BioMart \\
        -c "${params.outDir}/requests_cache" \\
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
    echo -e "original_id\tgene_name\tsource" > gene_name_concat.tsv && grep -h . ${tsvFiles} >> gene_name_concat.tsv
    """
}
