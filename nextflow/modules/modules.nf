process RUN_FASTQC {
    conda "${params.condaEnv}"
    publishDir "${params.outDir}/fastqc", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(reads)

    output:
    path "${sampleId}", emit: logs

    script:
    """
    bash ${params.scriptDir}/run_fastqc.sh "$sampleId" "$reads"
    """
}

process RUN_FASTQC_SUBDIR {
    conda "${params.condaEnv}"
    publishDir "${params.outDir}/fastqc/${subdir}", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(reads)
    val subdir

    output:
    path "${sampleId}", emit: logs

    script:
    """
    bash ${params.scriptDir}/run_fastqc.sh "$sampleId" "$reads"
    """
}

process RUN_MULTIQC {
    conda "${params.condaEnv}"
    publishDir "${params.outDir}", mode: 'copy', overwrite: false

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

process RUN_FASTP {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/fastq", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(reads)
    path adapterFASTA

    output:
    tuple val(sampleId), path('*.fastp.fastq.gz') , optional:true, emit: reads
    tuple val(sampleId), path('*.json'), emit: json
    tuple val(sampleId), path('*.html'), emit: html
    tuple val(sampleId), path('*.log'), emit: log

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

process STAR_ALIGN {
    label 'process_high'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/aligned", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(reads)

    output:
    tuple val(sampleId), path('*Log.final.out')   , emit: log_final
    tuple val(sampleId), path('*Log.out')         , emit: log_out
    tuple val(sampleId), path('*Log.progress.out'), emit: log_progress
    tuple val(sampleId), path('*d.out.bam')              , optional:true, emit: bam
    tuple val(sampleId), path('*sortedByCoord.out.bam')  , optional:true, emit: bam_sorted
    tuple val(sampleId), path('*toTranscriptome.out.bam'), optional:true, emit: bam_transcript
    tuple val(sampleId), path('*Aligned.unsort.out.bam') , optional:true, emit: bam_unsorted
    tuple val(sampleId), path('*fastq.gz')               , optional:true, emit: fastq
    tuple val(sampleId), path('*.tab')                   , optional:true, emit: tab
    tuple val(sampleId), path('*.SJ.out.tab')            , optional:true, emit: spl_junc_tab
    tuple val(sampleId), path('*.ReadsPerGene.out.tab')  , optional:true, emit: read_per_gene_tab
    tuple val(sampleId), path('*.out.junction')          , optional:true, emit: junction
    tuple val(sampleId), path('*.out.sam')               , optional:true, emit: sam
    tuple val(sampleId), path('*.wig')                   , optional:true, emit: wig
    tuple val(sampleId), path('*.bg')                    , optional:true, emit: bedgraph

    script:
    """
    STAR \\
        --genomeDir ${params.genomeDir} \\
        --readFilesIn ${reads[0]} ${reads[1]} \\
        --runThreadN $task.cpus \\
        --outFileNamePrefix ${sampleId}. \\
        --readFilesCommand zcat \\
        --twopassMode Basic \\
        --sjdbOverhang 100 \\
        --outFilterType BySJout \\
        --outFilterMultimapNmax 20 \\
        --alignSJoverhangMin 8 \\
        --alignSJDBoverhangMin 1 \\
        --outFilterMismatchNmax 999 \\
        --outFilterMismatchNoverReadLmax 0.04 \\
        --alignIntronMin 20 \\
        --alignIntronMax 1000000 \\
        --alignMatesGapMax 1000000 \\
        --outSAMtype BAM SortedByCoordinate
    """
}

process SAMTOOLS_INDEX {
    label 'process_low'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/aligned", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.bai") , emit: bai

    script:
    """
    samtools \\
        index \\
        -@ ${task.cpus-1} \\
        ${bam}
    """
}

process SAMTOOLS_FLAGSTAT {
    label 'process_single'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/alignment", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.flagstat") , emit: flagstat

    script:
    """
    samtools \\
        flagstat \\
        --threads ${task.cpus} \\
        ${bam} \\
        > ${sampleId}.flagstat
    """
}

process GET_BED {
    publishDir "${params.outDir}", mode: 'copy', overwrite: false

    output:
    path '*.bed*', emit: bed

    shell:
    """
    wget -O "!{params.fileBED}" "!{params.linkBED}"
    """
}

process RSEQC_BAMSTAT {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/rseqc", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.bam_stat.txt"), emit: txt

    script:
    """
    bam_stat.py \\
        -i ${bam} \\
        > ${sampleId}.bam_stat.txt
    """
}

process RSEQC_INFEREXP {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/rseqc", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)
    path bed

    output:
    tuple val(sampleId), path("*.infer_experiment.txt"), emit: txt

    script:
    """
    infer_experiment.py \\
        -i ${bam} \\
        -r ${bed} \\
        > ${sampleId}.infer_experiment.txt
    """
}

process RSEQC_READDISTRIBUTION {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/rseqc", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)
    path bed

    output:
    tuple val(sampleId), path("*.read_distribution.txt"), emit: txt

    script:
    """
    read_distribution.py \\
        -i ${bam} \\
        -r ${bed} \\
        > ${prefix}.read_distribution.txt
    """
}

process RSEQC_READDUPLICATION {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.outDir}/rseqc", mode: 'copy', overwrite: false

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*seq.DupRate.xls"), emit: seq_xls
    tuple val(sampleId), path("*pos.DupRate.xls"), emit: pos_xls
    tuple val(sampleId), path("*.pdf")           , emit: pdf
    tuple val(sampleId), path("*.r")             , emit: rscript

    script:
    """
    read_duplication.py \\
        -i ${bam} \\
        -o ${sampleId}
    """
}
