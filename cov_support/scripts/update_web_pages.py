#!/usr/bin/env python3
import csv
import os
import argparse
import collections

def parse_args():
    parser = argparse.ArgumentParser(description='Update lineage web pages for cov-lineages.org')

    parser.add_argument("--assignment-dir", action="store", type=str, dest="assignment_dir")
    parser.add_argument("--website-dir", action="store", type=str, dest="website_dir")
    parser.add_argument('-i',"--lineages-csv", action="store",type=str, dest="lineages_csv")
    parser.add_argument('-n',"--lineages-notes", action="store",type=str, dest="lineages_notes")
    parser.add_argument('-s',"--summary-file", action="store",type=str, dest="summary_file")
    parser.add_argument("--summary-figures", action="store",type=str, dest="summary_figures")
    parser.add_argument("-o","--outfile",action="store",type=str, dest="outfile")
    return parser.parse_args()

def return_descriptions_text():
    # the preamble at the start of the descriptions page
    descriptions_text = """---\nlayout: page\ntitle: Lineage descriptions\nimage: assets/images/global_lineages_tree.png\n---\n\n\n\n<p>Lineages as described in Rambaut et al 2020, which the software tool pangolin assigns, are characterised by a combination of genetic and epidemiological support. This hierarchical, dynamic nomenclature describes a lineage as a cluster of sequences seen in a geographically distinct region with evidence of ongoing transmission in that region. Multiple sources of information are taken into account, including phylogenetic information as well as a variety of metadata associated with that sequence. For example, lineage B.4 was characterised as a lineage corresponding to the large outbreak in Iran early this year long any genome sequences from Iran were available due to travel history information associated with exported cases. The finer scale of this nomenclature system can help tease apart outbreak investigations and as rates of international travel increases will facilitate tracking viral imports across the globe.</p>\n\n<hr class="major" /><h3>Lineage links</h3>\n<p>\n\t<ul class="alt">\n\t\t"""
    return descriptions_text

def create_lineage_dict(lineage_csv):
    # add lineages and sub lineages into a dict keyed by lineage name, with associated lineage metadata
    lineage_dict = collections.defaultdict(list)

    with open(lineage_csv,"r") as f:
        for l in f:
            l = l.rstrip("\n")
            tokens = l.split(",")
            taxon,lineage = tokens
            if lineage != "lineage":
                for i in range(len(lineage.split("."))):
                    parents = ".".join(lineage.split(".")[:i+1])
                    lineage_dict[parents].append((lineage, l))
    return lineage_dict

def create_notes_dict(lineage_notes):
    # add lineages and sub lineages notes into a dict keyed by lineage name
    href_dict = {}
    just_href = {}
    lineage_notes = collections.defaultdict(list)
    with open(lineage_notes,"r") as f:
        for l in f:
            l = l.rstrip("\n")
            lineage,description = l.split("\t")
            if lineage != "lineage":
                href_dict[lineage] = """<a href="{{ 'lineages/lineage_""" + lineage + """.html' | absolute_url }}">""" + lineage + """</a>"""
                just_href[lineage] = """"{{ 'lineages/lineage_""" + lineage + """.html' | absolute_url }}"""
                for i in range(len(lineage.split("."))):
                    parents = ".".join(lineage.split(".")[:i+1])
                    lineage_notes[parents].append((lineage, description))
    return lineage_notes, href_dict, just_href

def make_summary_dict(summary_file):
    # add lineages and sub lineages into a dict with verity's summary information about each lineage
    summary_dict = collections.defaultdict(list)
    with open(summary_file,"r") as f:
        for l in f:
            l = l.rstrip("\n")
            tokens = l.split('\t')
            lineage = tokens[0].split("]")[0].lstrip('[')
            tokens[0] = lineage
            if lineage != "Lineage":
                for i in range(len(lineage.split("."))):
                    parents = ".".join(lineage.split(".")[:i+1])
                    summary_dict[parents].append((lineage, tokens))
    return summary_dict

def create_lineage_and_assignment_pages(outfile, website_dir,assignment_dir, summary_figures, lineage_dict, lineage_notes, summary_dict, href_dict, just_href):
    with open(outfile,"w") as fall:
        # write preamble to descriptions file
        descriptions_text = return_descriptions_text()
        fall.write(descriptions_text)

        # populating the assignment directory with metadata in a directory tree
        for lineage in sorted(lineage_dict):
            inter_dirs = [assignment_dir]
            for i in range(len(lineage.split("."))):
                parent = ".".join(lineage.split(".")[:i+1])
                inter_dirs.append(parent)

            parent_dir = "/".join(inter_dirs[:-1])
            parent_directory = os.path.join(parent_dir)
            if not os.path.exists(parent_directory):
                os.mkdir(parent_directory)
            
            with open(os.path.join(parent_directory,f"{lineage}.metadata.csv"), "w") as fw:
                fw.write("GISAID ID,name,country,travel history,sample date,epiweek,lineage,representative\n")
                print(lineage)
                for line in sorted(lineage_dict[lineage], key = lambda x : x[0]):
                    fw.write(line[1] + '\n')
            
            # write the descriptions to descriptions.md for each lineage, with hyperlinks
            descriptions = sorted(lineage_notes[lineage], key = lambda x : x[0])
            lin_desc = descriptions[0][1]
            fall.write("""<li>""" + href_dict[lineage] + """Lineage """ + lineage + f"""</a> <br>{lin_desc}<br></li>\n\t\t""")

            # create lineage webpage
            with open(os.path.join(web_dir, f"lineage_{lineage}.md"),"w") as fw:
                fw.write(f"""---\nlayout: page\ntitle: Lineage {lineage}\n---\n\n\n\n""")
                
                # for anything but A or B, create a hyperlink to the parent lineage at the top of the webpage
                if "." in lineage:
                    parent_lineage = ".".join(lineage.split(".")[:-1])
                    fw.write(f"""<p>\n<ul class="actions small">\n\t <a href=""" + just_href[parent_lineage] + """" class="button special fit">Go to parent lineage: """+parent_lineage+"""</a>\n</ul>\n</p>\n""")
                
                # get the lineage svg figures
                fw.write(f"<h3> Lineage summaries</h3>\n\n")
                os.system(f"cp {summary_figures}/{lineage}.svg {website_dir}/assets/images/{lineage}.svg")
                fw.write(f"""<img src="../assets/images/{lineage}.svg" alt="{lineage} lineage summary figure" width="90%" height="700px" />\n\n\n""")

                # write lineage summary information to a md table. 
                fw.write("""| Lineage name | Most common countries | Date range | Number of taxa |  Days since last sampling | Known Travel | Recall value |\n|:-----|:-----|:-------|-------:|-------:|:---------|--------:|\n""")
                for line in sorted(summary_dict[lineage], key = lambda x : x[0]):
                    items = line[1]
                    href = href_dict[items[0]]
                    table_items = " | ".join(items[1:])
                    fw.write(f"| {href} | {table_items} |\n")

                # write lineage descriptions to a md table. 
                fw.write("\n<h3>Lineage descriptions</h3>\n\n")
                fw.write(f"""| Lineage | Notes |\n|:-----|:-----|\n""")
                for d in descriptions:
                    lin = d[0]
                    link_lin = href_dict[lin]
                    fw.write(f"| {link_lin} | {d[1]} |\n")
                fw.write("\n")

        # finish off the main lineage descriptions webpage
        fall.write("</ul>\n</p>\n")

def update_pages():
    args = parse_args()

    lineage_dict = create_lineage_dict(args.lineage_csv)
    lineage_notes, href_dict, just_href = create_notes_dict(args.lineage_notes)
    summary_dict = make_summary_dict(args.summary_file)
    
    create_lineage_and_assignment_pages(args.outfile,args.website_dir,args.assignment_dir, args.summary_figures, lineage_dict, lineage_notes, summary_dict, href_dict, just_href)

if __name__ == '__main__':

    update_pages()
    