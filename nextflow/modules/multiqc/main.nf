process RUN_MULTIQC {
    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    val filename
    path '*'

    output:
    path "${filename}_multiqc_report"

    script:
    """
    multiqc . -o "${filename}_multiqc_report"
    """
}
