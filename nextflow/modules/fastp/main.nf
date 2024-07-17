process RUN_FASTP {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(reads)
    path adapterFASTA

    output:
    tuple val(sampleId), path('*.fastp.fastq.gz') , optional:true, emit: reads
    tuple val(sampleId), path('*.json')                          , emit: json
    tuple val(sampleId), path('*.html')                          , emit: html
    tuple val(sampleId), path('*.log')                           , emit: log

    script:
    def adapterList = adapterFASTA ? "--adapter_fasta ${adapterFASTA}" : ""
    """
    fastp \\
        --in1 ${reads[0]} \\
        --in2 ${reads[1]} \\
        --out1 ${sampleId}_1.fastp.fastq.gz \\
        --out2 ${sampleId}_2.fastp.fastq.gz \\
        --json ${sampleId}.fastp.json \\
        --html ${sampleId}.fastp.html \\
        --trim_poly_x \\
        $adapterList \\
        2> >(tee ${sampleId}.fastp.log >&2)
    """
}
