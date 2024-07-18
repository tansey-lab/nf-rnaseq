#!/usr/bin/env nextflow

/*
========================================================================================
    STAR RNA-Seq NextFlow Pipeline for Tansey Lab
========================================================================================
    Github   :  https://github.com/tansey-lab/nf-rnaseq
    Contact  :  Jess White
----------------------------------------------------------------------------------------
*/

params.max_memory = "64.GB"
params.max_cpus = 12

params.fastq = "${params.inputDir}${params.fastqFile}"

params.fastp = "${params.outDir}/fastp/*_{1,2}.fastp*"
params.fastp_json = "${params.outDir}/fastp/*fastp.json"

params.fastqc_fastq = "${params.outDir}/fastqc/fastq/*/*"
params.fastqc_fastp = "${params.outDir}/fastqc/fastp/*/*"

params.bam = "${params.outDir}/aligned/*.Aligned.sortedByCoord.out.bam"

log.info """\
        STAR RNA-Seq NextFlow Pipeline (Reference-Based)
        =================================================
        inputDir     : ${params.inputDir}
        outDir       : ${params.outDir}
        condaEnv     : ${params.condaEnv}

        genomeDir    : ${params.genomeDir}
        adapterFASTA : ${params.adapterFASTA}
        fileBED      : ${params.fileBED}
        """
        .stripIndent()

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// pre-trimming QC fastqc and multiqc
include { RUN_FASTQC  as RUN_FASTQC_FASTQ  } from './modules/fastqc/main.nf'   addParams(OUTPUT: "${params.outDir}/fastqc/fastq")
include { RUN_MULTIQC as RUN_MULTIQC_FASTQ } from './modules/multiqc/main.nf'  addParams(OUTPUT: "${params.outDir}/multiqc/fastq")

// trimming with fastp and pre-alignment QC fastqc and multiqc
include { RUN_FASTP                        } from './modules/fastp/main.nf'    addParams(OUTPUT: "${params.outDir}/fastp")
include { RUN_FASTQC  as RUN_FASTQC_FASTP  } from './modules/fastqc/main.nf'   addParams(OUTPUT: "${params.outDir}/fastqc/fastp")
include { RUN_MULTIQC as RUN_MULTIQC_FASTP } from './modules/multiqc/main.nf'  addParams(OUTPUT: "${params.outDir}/multiqc/fastp")

// align fastq files using STAR and index
include { STAR_ALIGN                       } from './modules/star/main.nf'     addParams(OUTPUT: "${params.outDir}/alignment")
include { SAMTOOLS_INDEX                   } from './modules/samtools/main.nf' addParams(OUTPUT: "${params.outDir}/alignment")

// post-alignment multiqc
include { RUN_MULTIQC as RUN_MULTIQC_STAR  } from './modules/multiqc/main.nf'  addParams(OUTPUT: "${params.outDir}/multiqc/bam")

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { BAM_QC } from './subworkflows/bam_qc.nf' addParams(OUTPUT: "${params.outDir}/bamqc")

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    LOAD FILES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

Channel
    .fromFilePairs ( params.fastq, checkIfExists: true )
    .set { fastq_ch }

if ( params.adapterFASTA ){
    adapter_fasta = file(params.adapterFASTA)
    if( !adapter_fasta.exists() ) exit 1, "Genome chrom sizes file not found: ${params.adapterFASTA}"
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    WORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow FASTQC_FASTQ {
    RUN_FASTQC_FASTQ ( fastq_ch )
    RUN_MULTIQC_FASTQ (
        "fastq",
        RUN_FASTQC_FASTQ.out.logs.collect()
    )
}

workflow FASTP_FASTQ {
    RUN_FASTP ( fastq_ch, adapter_fasta )
    RUN_FASTQC_FASTP ( RUN_FASTP.out.reads )
    RUN_MULTIQC_FASTP (
        "fastp",
        RUN_FASTQC_FASTP.out.logs.mix(
            RUN_FASTP.out.json.map { it -> it[1] }
        ).collect()
    )
}

workflow STAR_FASTQ {
    Channel
        .fromFilePairs ( params.fastp, checkIfExists: true )
        .set { fastp_ch }

    STAR_ALIGN ( fastp_ch )
    SAMTOOLS_INDEX ( STAR_ALIGN.out.bam_sorted )
}

workflow QC_BAM {
    Channel
        .fromPath ( params.bam, checkIfExists: true )
        .map { [it.simpleName, it ] }
        .set { bam_ch }

    BAM_QC ( bam_ch )

    Channel
        .fromPath ( params.fastp_json, checkIfExists: true )
        .set { fastp_json_ch }

    Channel
        .fromPath ( params.fastqc_fastp, checkIfExists: true )
        .set { fastqc_ch }

    fastp_json_ch.concat(
        fastqc_ch,
        BAM_QC.out.flagstat.map { it -> it[1] },
        BAM_QC.out.bamstat.map { it -> it[1] },
        BAM_QC.out.inferexp.map { it -> it[1] },
        BAM_QC.out.readdup.map { it -> it[1] },
        BAM_QC.out.readdist.map { it -> it[1] }
    ).set { qc_ch }

    RUN_MULTIQC_STAR (
        "bam",
        qc_ch.collect()
    )
}

workflow.onComplete {

    println ( workflow.success ? """
        Pipeline execution summary
        ---------------------------
        Completed at: ${workflow.complete}
        Duration    : ${workflow.duration}
        Success     : ${workflow.success}
        workDir     : ${workflow.workDir}
        exit status : ${workflow.exitStatus}
        """ : """
        Failed: ${workflow.errorReport}
        exit status : ${workflow.exitStatus}
        """
    )
}

/*
========================================================================================
    THE END
========================================================================================
*/
