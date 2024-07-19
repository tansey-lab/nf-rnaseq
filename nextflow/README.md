# NextFlow workflow to run bulk RNA-seq pipeline

## Getting started

To run the pipeline on Iris use: `nextflow run main.nf -params-file params.json -profile iris`

It is recommended that each workflow in `main.nf` is run sequentially to allow for users to inspect intermediate QC results and select optimal parameters for downstream tasks:

1. **Initial QC**
    - The first workflow runs [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on the raw fastq files and then [`MultiQC`](http://multiqc.info/) on those results
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTQC_FASTQ`

2. **Trimming and QC**
    - The second workflow runs [`fastp`](https://github.com/OpenGene/fastp) to trim adapters and/or poly-X or poly-A tails, followed by [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [`MultiQC`](http://multiqc.info/)
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTP_FASTQ`

3. **Alignment and indexing**
    - The third workflow runs [`STAR`](https://github.com/alexdobin/STAR) on the adapter-trimmed fastq files followed by [`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) indexing
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry STAR_FASTQ`

4. **Post-alignment QC**
    - The fourth workflow runs QC on the resulting BAM files ([`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) `flagstat` and various [`RSeQC`](http://rseqc.sourceforge.net/) modules), followed by [`MultiQC`](http://multiqc.info/) on those results
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry QC_BAM`

## Environment

Currently, this workflow assumes that a `conda` environment has been created with all necessary packages (TODO: add yml file).

## Contents of `params.json`

Generate own `params.json` file using the following parameters:
```
{
    "inputDir"     : "TODO",
    "fastqFile"    : "TODO",
    "outDir"       : "TODO",
    "condaEnv"     : "TODO",
    "genomeDir"    : "TODO",
    "adapterFASTA" : "TODO",
    "linkBED"      : "TODO",
    "fileBED"      : "TODO"
}
```

Below is a description of what each variable should contain. If variable is optional and not in use, do not create any entry in the `json` file.

| Variable     | Optional | Description                                                      |
| :------------| :------: | :----------------------------------------------------------------|
| inputDir     |    No    | Input directory where fastq files reside                         |
| fastq        |    No    | FASTQ file naming pattern with wildcards within inputDir         |
| outDir       |    No    | Output directory where results are saved                         |
| condaEnv     |    No    | Path to conda environment to use                                 |
| genomeDir    |    No    | Path to STAR genome directory to use for alignment               |
| adapterFASTA |    Yes   | FASTA file containing adapters to trim with FASTP                |
| linkBED      |    Yes   | Link to bed file to use; only necessary with some RSeqQC modules |
| fileBED      |    Yes   | Bed file name to use; only necessary with some RSeqQC modules    |

## Output directory/file structure

The following is the directory and file structure that will be generated if paired end fastq files with naming convention `<sampleId>_R{1,2}.fastq` are used as a starting point and all workflows are run:

TODO: Add `bam_multiqc_report` and any quantification (`RSEM`/`featureCounts`) outputs once finished running.

```
├── alignment
│   ├── <sampleId>.Aligned.sortedByCoord.out.bam
│   ├── <sampleId>.Aligned.sortedByCoord.out.bam.bai
│   ├── <sampleId>.Log.final.out
│   ├── <sampleId>.Log.out
│   ├── <sampleId>.Log.progress.out
│   ├── <sampleId>.SJ.out.tab
├── bamqc
│   ├── <sampleId>.bam_stat.txt
│   ├── <sampleId>.DupRate_plot.pdf
│   ├── <sampleId>.DupRate_plot.r
│   ├── <sampleId>.flagstat
│   ├── <sampleId>.infer_experiment.txt
│   ├── <sampleId>.pos.DupRate.xls
│   ├── <sampleId>.read_distribution.txt
│   ├── <sampleId>.seq.DupRate.xls
├── fastp
│   ├── <sampleId>_1.fastp.fastq.gz
│   ├── <sampleId>_2.fastp.fastq.gz
│   ├── <sampleId>.fastp.html
│   ├── <sampleId>.fastp.json
│   ├── <sampleId>.fastp.log
├── fastqc
│   ├── fastp
│   │   ├── <sampleId>
│   │   │   ├── <sampleId>_1.fastp_fastqc.html
│   │   │   ├── <sampleId>_1.fastp_fastqc.zip
│   │   │   ├── <sampleId>_2.fastp_fastqc.html
│   │   │   └── <sampleId>_2.fastp_fastqc.zip
│   └── fastq
│       ├── <sampleId>
│       │   ├── <sampleId>_R1_fastqc.html
│       │   ├── <sampleId>_R1_fastqc.zip
│       │   ├── <sampleId>_R2_fastqc.html
│       │   └── <sampleId>_R2_fastqc.zip
├── <fileBED>.bed
├── multiqc
│   ├── fastp_multiqc_report
│   │   ├── multiqc_data
│   │   │   ├── fastp_filtered_reads_plot.txt
│   │   │   ├── fastp-insert-size-plot.txt
│   │   │   ├── fastp-seq-content-gc-plot_Read_1_After_filtering.txt
│   │   │   ├── fastp-seq-content-gc-plot_Read_1_Before_filtering.txt
│   │   │   ├── fastp-seq-content-gc-plot_Read_2_After_filtering.txt
│   │   │   ├── fastp-seq-content-gc-plot_Read_2_Before_filtering.txt
│   │   │   ├── fastp-seq-content-n-plot_Read_1_After_filtering.txt
│   │   │   ├── fastp-seq-content-n-plot_Read_1_Before_filtering.txt
│   │   │   ├── fastp-seq-content-n-plot_Read_2_After_filtering.txt
│   │   │   ├── fastp-seq-content-n-plot_Read_2_Before_filtering.txt
│   │   │   ├── fastp-seq-quality-plot_Read_1_After_filtering.txt
│   │   │   ├── fastp-seq-quality-plot_Read_1_Before_filtering.txt
│   │   │   ├── fastp-seq-quality-plot_Read_2_After_filtering.txt
│   │   │   ├── fastp-seq-quality-plot_Read_2_Before_filtering.txt
│   │   │   ├── fastqc_adapter_content_plot.txt
│   │   │   ├── fastqc_overrepresented_sequences_plot.txt
│   │   │   ├── fastqc_per_base_n_content_plot.txt
│   │   │   ├── fastqc_per_base_sequence_quality_plot.txt
│   │   │   ├── fastqc_per_sequence_gc_content_plot_Counts.txt
│   │   │   ├── fastqc_per_sequence_gc_content_plot_Percentages.txt
│   │   │   ├── fastqc_per_sequence_quality_scores_plot.txt
│   │   │   ├── fastqc_sequence_counts_plot.txt
│   │   │   ├── fastqc_sequence_duplication_levels_plot.txt
│   │   │   ├── fastqc_sequence_length_distribution_plot.txt
│   │   │   ├── fastqc-status-check-heatmap.txt
│   │   │   ├── fastqc_top_overrepresented_sequences_table.txt
│   │   │   ├── multiqc_citations.txt
│   │   │   ├── multiqc_data.json
│   │   │   ├── multiqc.log
│   │   │   └── multiqc_sources.txt
│   │   └── multiqc_report.html
│   └── fastq_multiqc_report
│       ├── multiqc_data
│       │   ├── fastqc_adapter_content_plot.txt
│       │   ├── fastqc_overrepresented_sequences_plot.txt
│       │   ├── fastqc_per_base_n_content_plot.txt
│       │   ├── fastqc_per_base_sequence_quality_plot.txt
│       │   ├── fastqc_per_sequence_gc_content_plot_Counts.txt
│       │   ├── fastqc_per_sequence_gc_content_plot_Percentages.txt
│       │   ├── fastqc_per_sequence_quality_scores_plot.txt
│       │   ├── fastqc_sequence_counts_plot.txt
│       │   ├── fastqc_sequence_duplication_levels_plot.txt
│       │   ├── fastqc-status-check-heatmap.txt
│       │   ├── fastqc_top_overrepresented_sequences_table.txt
│       │   ├── multiqc_citations.txt
│       │   ├── multiqc_data.json
│       │   ├── multiqc_general_stats.txt
│       │   ├── multiqc.log
│       │   └── multiqc_sources.txt
│       └── multiqc_report.html
├── pipeline_info
│   ├── execution_report_<yyyy-MM-dd_HH-mm-ss>.html
│   ├── execution_timeline_<yyyy-MM-dd_HH-mm-ss>.html
│   ├── execution_trace_<yyyy-MM-dd_HH-mm-ss>.txt
│   ├── pipeline_dag_<yyyy-MM-dd_HH-mm-ss>.html
```
