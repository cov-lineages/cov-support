import os

rule gisaid_process_json:
    input:
        json = config["latest_gisaid_json"],
        omitted = config["previous_omitted_file"],
        metadata = config["previous_gisaid_metadata"]
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.fasta"),
        metadata = os.path.join(config["output_path"], "/0/gisaid.csv")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_process_json.log")
    shell:
        """
        datafunk process_gisaid_data \
          --input-json \"{input.json}\" \
          --input-metadata \"{input.metadata}\" \
          --exclude-file \"{input.omitted}\" \
          --output-fasta {output.fasta} \
          --output-metadata {output.metadata} \
          --exclude-undated &> {log}
        """

rule gisaid_unify_headers:
    input:
        fasta = rules.gisaid_process_json.output.fasta,
        metadata = rules.gisaid_process_json.output.metadata
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.UH.fasta"),
        metadata = os.path.join(config["output_path"], "/0/gisaid.UH.csv")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_unify_headers.log")
    shell:
        """
        datafunk set_uniform_header \
          --input-fasta {input.fasta} \
          --input-metadata {input.metadata} \
          --output-fasta {output.fasta} \
          --output-metadata {output.metadata} \
          --log {log} \
          --gisaid
        """


rule gisaid_remove_duplicates:
    input:
        fasta = rules.gisaid_unify_headers.output.fasta,
        metadata = rules.gisaid_unify_headers.output.metadata
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.UH.RD.fasta"),
        metadata = os.path.join(config["output_path"], "/0/gisaid.UH.RD.csv")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_filter_duplicates.log")
    shell:
        """
        fastafunk subsample \
          --in-fasta {input.fasta} \
          --in-metadata {input.metadata} \
          --group-column sequence_name \
          --index-column sequence_name \
          --out-fasta {output.fasta} \
          --sample-size 1 \
          --out-metadata {output.metadata} \
          --select-by-min-column edin_epi_week &> {log}
        """


rule gisaid_counts_by_country:
    input:
        metadata = rules.gisaid_remove_duplicates.output.metadata
    output:
        counts = os.path.join(config["output_path"], "/0/gisaid_counts_by_country.csv"),
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_counts_by_country.log")
    shell:
        """
        fastafunk count \
          --in-metadata {input.metadata} \
          --group-column edin_admin_0 \
          --log-file {output.counts} &> {log}
        """


rule gisaid_filter_1:
    input:
        fasta = rules.gisaid_remove_duplicates.output.fasta
    params:
        min_covg = config["min_covg"],
        min_length = config["min_length"]
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.RD.UH.filt1.fasta")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_filter_1.log")
    shell:
        """
        datafunk filter_fasta_by_covg_and_length \
          -i {input.fasta} \
          -o {output} \
          --min-length {params.min_length} &> {log}
        """


rule gisaid_minimap2_to_reference:
    input:
        fasta = rules.gisaid_filter_1.output.fasta,
        reference = config["reference_fasta"]
    output:
        sam = os.path.join(config["output_path"], "/0/gisaid.mapped.sam")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_minimap2_to_reference.log")
    shell:
        """
        minimap2 -a -x asm5 {input.reference} {input.fasta} -o {output} &> {log}
        """


rule gisaid_remove_insertions_and_pad:
    input:
        sam = rules.gisaid_minimap2_to_reference.output.sam,
        reference = config["reference_fasta"]
    params:
        trim_start = config["trim_start"],
        trim_end = config["trim_end"],
        insertions = os.path.join(config["output_path"], "/0/gisaid_insertions.txt")
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.RD.UH.filt1.mapped.fasta")
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_remove_insertions_and_pad.log")
    shell:
        """
        datafunk sam_2_fasta \
          -s {input.sam} \
          -r {input.reference} \
          -o {output} \
          -t [{params.trim_start}:{params.trim_end}] \
          --pad \
          --log-inserts &> {log}
        mv insertions.txt {params.insertions}
        """


rule gisaid_filter_2:
    input:
        fasta = rules.gisaid_remove_insertions_and_pad.output.fasta
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.RD.UH.filt.mapped.filt2.fasta")
    params:
        min_covg = config["min_covg"]
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_filter_2.log")
    shell:
        """
        datafunk filter_fasta_by_covg_and_length \
          -i {input.fasta} \
          -o {output.fasta} \
          --min-covg {params.min_covg} &> {log}
        """

rule gisaid_mask:
    input:
        fasta = rules.gisaid_filter_2.output.fasta,
        mask = config["gisaid_mask_file"]
    output:
        fasta = os.path.join(config["output_path"], "/0/gisaid.RD.UH.filt.mapped.filt2.masked.fasta"),
    shell:
        """
        datafunk mask \
          --input-fasta {input.fasta} \
          --output-fasta {output.fasta} \
          --mask-file \"{input.mask}\"
        """


rule gisaid_distance_QC:
    input:
        fasta = rules.gisaid_mask.output.fasta,
        metadata = rules.gisaid_remove_duplicates.output.metadata
    log:
        os.path.join(config["output_path"], "/logs/0_gisaid_distance_QC.log")
    output:
        table = os.path.join(config["output_path"], "/0/QC_distances.tsv"),
        fasta = 
    shell:
        """
        datafunk distance_to_root \
          --input-fasta {input.fasta} \
          --input-metadata {input.metadata} &> {log}
        mv distances.tsv {output.table}
        """
