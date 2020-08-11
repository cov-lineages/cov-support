
rule all:
    input:
        os.path.join(config["website_dir"], "descriptions.md")

rule make_summary_figures:
    input:
        metadata = config["lineages_metadata"],
        country_coordinates = config["country_coordinates"]
    params:
        outdir = config["summary_figures_dir"]
    output:
        os.path.join(config["data_dir"],"figure_prompt.txt")
    run:
        shell("""
        lineage_distributions.R {input.metadata} {input.country_coordinates} {params.outdir}""")
        shell("""mv *.svg {params.outdir} && touch {output}""")

rule make_summary_table:
    input:
        metadata = config["metadata"],
        recall = config["recall_file"]
    params:
        data_dir = config["data_dir"]
    output:
        table = os.path.join(config["data_dir"], "lineage_summary.tsv")
    shell:
        """
        make_summary_table.py \
        -m {input.metadata:q} \
        -r {input.recall:q} \
        -d {params.data_dir:q}
        """

rule update_web_pages:
    input:
        figure_prompt = os.path.join(config["data_dir"],"figure_prompt.txt"),
        lineages_csv = config["metadata"],
        summary_file = rules.make_summary_table.output.table,
        lineages_notes = config["descriptions"]
    params:
        assignment_dir = config["assignment_dir"],
        website_dir = config["website_dir"],
        summary_figures = config["summary_figures_dir"]
    output:
        descriptions_file = os.path.join(config["website_dir"], "descriptions.md")
    shell:
        """
        update_web_pages.py \
            --assignment-dir {params.assignment_dir:q} \
            --website-dir {params.website_dir:q} \
            --summary-figures {params.summary_figures:q} \
            --summary-file {input.summary_file:q} \
            -i {input.lineages_csv:q} \
            -n {input.lineages_notes:q} \
            -o {output.descriptions_file:q}
        """