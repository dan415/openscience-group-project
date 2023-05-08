
<h1> Tests</h1>

The approach is to execute the program changing the input files folder to test for different types of input.

Metrics can be obtained from the summary.json file to check if the program is working correctly.

Preconditions:
    Grobid must be running, dependencies must be installed and environment must be activated.
    Details on how to do this can be found in the README.md file of deliverable1.


<h2>Run</h2>
on folder deliverables_ai_open_science:

    python -m unittest deliverable1.test.test_analyzer

<h2>test_01_blank_pdf</h2>

*case_01*

Run with blank pdf file. 

Should output empty "figures.png", "links.txt" and "summary.json", but no wordcloud.

Should not produce any exceptions.

If run with docker-compose, tei file will be generated, else it will not.

<h2>test_02_correct_num_papers</h2>

*case_02*

Run with 3 valid pdfs.

Should output 7 files, and produce no exceptions

<h2>test_03_correct_num_figures</h2>

*case_03*

Run with 4 valid pdfs, total number of figures in summary.json should be 25.

Should not produce any exceptions.

<h2>test_03_correct_num_links</h2>

*case_03*

Run with 4 valid pdfs, total number of links in summary.json should be 8.

Should not produce any exceptions.
