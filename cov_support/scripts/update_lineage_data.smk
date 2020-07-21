rule make_summary_figures:
    input:
        metadata = 
        assignments = 
    params:
        outdir = config["summary_figures_dir"]
    output:
        
    shell:
        """
        chris_script.R
        """

rule make_summary_table:
    input:
        metadata = 
        assignment = 
        pmd = 
    output:
        table = os.path.join(config["data_dir"], "lineage_summary.tsv")
    shell:
        """
        verity_script.py
        """

rule update_web_pages:
    input:
        lineages_csv = os.path.join(config["data_dir"], "lineages.metadata.csv"),
        summary_file = rules.make_summary_table.output.table,
        lineages_notes = os.path.join(config["data_dir"], "lineages.descriptions.csv")
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