RDF extraction is a tool to read and create triples for materials experimental data.
This involves below steps:
1. Assigning a lables from ontology to the expermental data.
2. Creating RDF triples which involves class labels and meta data.

The tool is written in Python and it uses Flask as backend & frontend services.
The tool has following rest end points:
    
    a. ./file_read : to read the  ontology file(turtle file) and csv file(experimental data)
    b. ./data : to assign class labels 
