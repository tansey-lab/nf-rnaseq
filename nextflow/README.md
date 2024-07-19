# NextFlow workflow to run bulk RNA-seq pipeline

## Getting started

To run the pipeline on Iris use: `nextflow run main.nf -params-file params.json -profile iris`

It is recommended that each workflow in `main.nf` is run sequentially to allow for users to inspect intermediate QC results and select optimal parameters for downstream tasks:

1. **Initial QC**
    - The first workflow runs [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on the raw fastq files and then [`MultiQC`](http://multiqc.info/) on those results
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTQC_FASTQ`

```mermaid
<html>
<head>
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
</head>
<body>
<pre class="mermaid" style="text-align: center;">
flowchart TB
    subgraph " "
    v0["Channel.fromFilePairs"]
    v1["Channel.fromPath"]
    v3["adapterFASTA"]
    v11["filename"]
    end
    subgraph " "
    v2["adapter_ch"]
    v5[" "]
    v6[" "]
    v13[" "]
    end
    subgraph FASTP_FASTQ
    v4([RUN_FASTP])
    v7([RUN_FASTQC_FASTP])
    v12([RUN_MULTIQC_FASTP])
    v8(( ))
    end
    v0 --> v4
    v1 --> v2
    v3 --> v4
    v4 --> v7
    v4 --> v6
    v4 --> v5
    v4 --> v8
    v7 --> v8
    v11 --> v12
    v8 --> v12
    v12 --> v13

</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
</body>
</html>
```

2. **Trimming and QC**
    - The second workflow runs [`fastp`](https://github.com/OpenGene/fastp) to trim adapters and/or poly-X or poly-A tails, followed by [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [`MultiQC`](http://multiqc.info/)
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTP_FASTQ`

```mermaid
<html>
<head>
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
</head>
<body>
<pre class="mermaid" style="text-align: center;">
flowchart TB
    subgraph " "
    v0["Channel.fromFilePairs"]
    v1["Channel.fromPath"]
    v3["adapterFASTA"]
    v11["filename"]
    end
    subgraph " "
    v2["adapter_ch"]
    v5[" "]
    v6[" "]
    v13[" "]
    end
    subgraph FASTP_FASTQ
    v4([RUN_FASTP])
    v7([RUN_FASTQC_FASTP])
    v12([RUN_MULTIQC_FASTP])
    v8(( ))
    end
    v0 --> v4
    v1 --> v2
    v3 --> v4
    v4 --> v7
    v4 --> v6
    v4 --> v5
    v4 --> v8
    v7 --> v8
    v11 --> v12
    v8 --> v12
    v12 --> v13

</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
</body>
</html>
```

3. **Alignment and indexing**
    - The third workflow runs [`STAR`](https://github.com/alexdobin/STAR) on the adapter-trimmed fastq files followed by [`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) indexing
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry STAR_FASTQ`

```mermaid
<html>
<head>
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
</head>
<body>
<pre class="mermaid" style="text-align: center;">
flowchart TB
    subgraph " "
    v0["Channel.fromFilePairs"]
    v1["Channel.fromPath"]
    v3["adapterFASTA"]
    v11["filename"]
    end
    subgraph " "
    v2["adapter_ch"]
    v5[" "]
    v6[" "]
    v13[" "]
    end
    subgraph FASTP_FASTQ
    v4([RUN_FASTP])
    v7([RUN_FASTQC_FASTP])
    v12([RUN_MULTIQC_FASTP])
    v8(( ))
    end
    v0 --> v4
    v1 --> v2
    v3 --> v4
    v4 --> v7
    v4 --> v6
    v4 --> v5
    v4 --> v8
    v7 --> v8
    v11 --> v12
    v8 --> v12
    v12 --> v13

</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
</body>
</html>
```

4. **Post-alignment QC**
    - The fourth workflow runs QC on the resulting BAM files ([`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) `flagstat` and various [`RSeQC`](http://rseqc.sourceforge.net/) modules), followed by [`MultiQC`](http://multiqc.info/) on those results
    - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry QC_BAM`

```mermaid
<html>
<head>
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1">
</head>
<body>
<pre class="mermaid" style="text-align: center;">
flowchart TB
    subgraph " "
    v0["Channel.fromFilePairs"]
    v2["Channel.fromPath"]
    v13["Channel.fromPath"]
    v14["Channel.fromPath"]
    v22["filename"]
    end
    subgraph " "
    v1["fastq_ch"]
    v9[" "]
    v10[" "]
    v11[" "]
    v24[" "]
    end
    subgraph QC_BAM
    subgraph BAM_QC
    v4([GET_BED])
    v5([SAMTOOLS_FLAGSTAT])
    v6([RSEQC_BAMSTAT])
    v7([RSEQC_INFEREXP])
    v8([RSEQC_READDUPLICATION])
    v12([RSEQC_READDISTRIBUTION])
    v3(( ))
    end
    v23([RUN_MULTIQC_STAR])
    v15(( ))
    end
    v0 --> v1
    v2 --> v3
    v4 --> v7
    v4 --> v12
    v3 --> v5
    v5 --> v15
    v3 --> v6
    v6 --> v15
    v3 --> v7
    v7 --> v15
    v3 --> v8
    v8 --> v11
    v8 --> v10
    v8 --> v9
    v8 --> v15
    v3 --> v12
    v12 --> v15
    v13 --> v15
    v14 --> v15
    v22 --> v23
    v15 --> v23
    v23 --> v24

</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
</body>
</html>
```

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
| fileBED      |    Yes   | Path to bed file to use; only necessary with some RSeqQC modules |

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
