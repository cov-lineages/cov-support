rule prep_data:
    input:
    
    output:

    shell:

rule run_training:
    input:
    
    output:

    shell:

rule get_per_lineage_rate:
    input:

    output:

    shell:

rule get_snps_with_signal:
    input:

    output:

    shell:

rule publish_trained_model:
    input:

    output:

    #to pangoLEARN repository
    shell:
    "cp {input} {output}"
