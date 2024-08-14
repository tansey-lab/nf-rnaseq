process QUERY_API {
    conda "${params.condaEnv}"

    input:
    val(inputIds)
    val(database)

    output:
    path("*.tsv"), emit: geneTSV

    script:
    def uuid = UUID.randomUUID().toString()
    """
    get_gene_name \\
        -i "${inputIds}" \\
        -d ${database} \\
        -c "${params.outDir}/requests_cache" \\
        -t \\
        > ${uuid}.tsv
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
