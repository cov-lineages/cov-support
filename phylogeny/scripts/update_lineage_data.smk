rule populate_assignment_repo:
    input:
        "lineages.csv"
    output:
        "summary"
    shell:
        """
        populate the directory of trees in the assignment repo
        """

rule make_summary_figures:
    input:
        metadata = 
        assignments = 
    output:
        figures
    shell:
        """
        chris_script.R
        """

rule make_summary_table:
    input:
        metadata = 
        assignment = 
    output:
        tables = 
    shell:
        """
        verity's script
        """

rule update_web_pages:
    input:
        summary_figures = 
        summary_tables = 
    output:
        html
    shell:
        """
        run script to update html pages per lineage
        """