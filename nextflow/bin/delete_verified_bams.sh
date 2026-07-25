#!/bin/bash
#
# Delete source BAMs that CRAM_BAM has verified as losslessly converted.
#
# This is deliberately NOT part of the Nextflow workflow. Nextflow stages
# process inputs as symlinks into the work directory, so deleting "the input"
# from inside a task either removes a symlink (no space reclaimed) or, if the
# real path is resolved, destroys source data during a run that -resume may
# later want to repeat. Deletion is a one-way operation and belongs in a step a
# human reviews and runs once.
#
# Usage:
#   delete_verified_bams.sh <manifest.tsv> <cramGenome>            # dry run, cheap checks
#   delete_verified_bams.sh <manifest.tsv> <cramGenome> --execute  # delete (re-verifies md5)
#
# --execute re-decodes every CRAM to confirm its md5 still matches the manifest
# before removing the only other copy. That is deliberately expensive - decoding
# ~30 GiB of CRAM takes minutes - so run it under sbatch, not on a login node.
# The dry run skips it and only checks that the files are where they should be.
#
set -euo pipefail

MANIFEST="${1:-}"
CRAM_GENOME="${2:-}"
MODE="${3:-dry-run}"
THREADS="${SLURM_CPUS_PER_TASK:-4}"

if [[ -z "$MANIFEST" || ! -f "$MANIFEST" ]]; then
    echo "usage: $0 <cram_verified_manifest.tsv> <cramGenome> [--execute]" >&2
    exit 1
fi

# CRAM cannot be decoded without the reference it was built against. Passing -T
# explicitly avoids samtools falling back to a REF_CACHE lookup or an outbound
# request to EBI, which on a compute node without internet would hang or fail.
if [[ -z "$CRAM_GENOME" || ! -f "$CRAM_GENOME" ]]; then
    echo "ERROR: cramGenome reference not found: ${CRAM_GENOME:-<unset>}" >&2
    exit 1
fi

CRAM_DIR="$(dirname "$(readlink -f "$MANIFEST")")"

total_freed=0
n_ok=0
n_skip=0

while IFS=$'\t' read -r sampleId src_bam bam_bytes cram_bytes cram_md5 status; do
    # skip header and the awk summary comment
    [[ "$sampleId" == "sampleId" || "$sampleId" == \#* ]] && continue
    [[ "$status" != "VERIFIED" ]] && { echo "SKIP (not verified): $sampleId"; n_skip=$((n_skip+1)); continue; }

    cram="${CRAM_DIR}/${sampleId}.cram"

    # re-check the published CRAM still exists and still matches the manifest
    # md5 before removing the only other copy of the data
    if [[ ! -f "$cram" ]]; then
        echo "SKIP (no published CRAM): $sampleId"; n_skip=$((n_skip+1)); continue
    fi
    if [[ ! -f "$src_bam" ]]; then
        echo "SKIP (source BAM already gone): $sampleId"; n_skip=$((n_skip+1)); continue
    fi

    if [[ "$MODE" == "--execute" ]]; then
        # only re-decode when actually about to delete something irreversible
        actual_md5=$(samtools view --threads "$THREADS" --input-fmt-option decode_md=0 \
            -T "$CRAM_GENOME" "$cram" | md5sum | cut -d' ' -f1)
        if [[ "$actual_md5" != "$cram_md5" ]]; then
            echo "SKIP (CRAM md5 drift, refusing to delete): $sampleId" >&2
            n_skip=$((n_skip+1)); continue
        fi
        rm -f "$src_bam" "${src_bam}.bai"
        echo "DELETED $src_bam"
    else
        # cheap sanity check only: CRAM present and non-empty
        if [[ ! -s "$cram" ]]; then
            echo "SKIP (empty CRAM): $sampleId"; n_skip=$((n_skip+1)); continue
        fi
        echo "WOULD DELETE $src_bam ($(numfmt --to=iec "$bam_bytes"))"
    fi
    total_freed=$((total_freed + bam_bytes))
    n_ok=$((n_ok+1))
done < "$MANIFEST"

echo
echo "----------------------------------------"
echo "eligible : $n_ok"
echo "skipped  : $n_skip"
echo "space    : $(numfmt --to=iec "$total_freed")"
[[ "$MODE" != "--execute" ]] && echo "DRY RUN - re-run with --execute to delete"
exit 0
