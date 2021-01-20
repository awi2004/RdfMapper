import flask_rdf
from flask import Flask, render_template, request, Response, flash
from rdflib.namespace import OWL, RDF, RDFS, FOAF
from flask_rdf.flask import returns_rdf
import rdflib
from flask import jsonify
import pandas as pd
import csv
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
from rdflib import ConjunctiveGraph, URIRef, RDFS, Literal
from flask_table import Table, Col
from flask import send_file
from wtforms import TextField, Form
import random

app = Flask(__name__)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

class_labels = []
class_labels_dict = {}
dictOfWordsFromCSV = {}
dictOfWordsHeaders = []
listOfWordsHeaders = []

# define graph
g = rdflib.Graph()

# set up a custom formatter to return turtle in text/plain to browsers
custom_formatter = flask_rdf.FormatSelector()
custom_formatter.wildcard_mimetype = 'text/plain'
custom_formatter.add_format('text/plain', 'turtle')
custom_decorator = flask_rdf.flask.Decorator(custom_formatter)


class SearchForm(Form):
    autocomp = TextField('class_labels', id='city_autocomplete')


@app.route('/rdf', methods=['GET', 'POST'])
def read_turte():
    """
    Read the turtle file
    :return: turtle class and literals.
    """
    file = request.form['upload-file']
    print(file)
    # no_of_rows = int(request.form['no_of_rows'])
    # g = rdflib.Graph()
    # g = ConjunctiveGraph()
    owlClass = rdflib.namespace.OWL.Class
    rdfType = rdflib.namespace.RDF.type

    result = g.parse(file, format="turtle")
    final_list = []
    # Iterate over triples in store and print them out
    # for s, p, o in result:
    #     # if type(o) == rdflib.term.Literal:
    #     # sub.append(s),prop.append(p),obj.append(o)
    #     # final_list.append((s, o))
    #     final_list.append((s, g.label(s)))
    for s in result.subjects(predicate=rdfType, object=owlClass):
        class_labels.append(result.label(s).title())
        final_list.append((s.title(), result.label(s).title()))
        class_labels_dict[result.label(s).title()] = s.title()
    labels = list(set([i for i in final_list if len(i[1]) > 0]))
    print(len(labels))
    # print(class_labels_dict)
    print(class_labels_dict.get('Computertomograph'))
    # print(class_labels_dict.get('DepthOfCut'))
    rdf_df = pd.DataFrame(labels, columns=['class(subject)', 'label(literals)'])

    return render_template('turtle_list.html', tables=[rdf_df.to_html(classes='data')],
                           titles=rdf_df.columns.values)
    # jsonify(final_list[0:no_of_rows])


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/file_read', methods=['GET', 'POST'])
def file_read():
    return render_template('index_old.html')


@app.route('/data', methods=['GET', 'POST'])
def data():
    """
    Read csv file.
    :return: data in CSV file.
    """

    dropdown_list = []
    if request.method == 'POST':
        file = request.form['upload-file']
        no_of_lines = int(request.form['no_of_rows_csv'])
        print(no_of_lines)
        # pprint(file) a
        # final_list= read_turte()

        with open(file, newline='') as fin:
            reader = csv.reader(fin, delimiter=";")
            csv_whole_list = list(reader)
            csv_list = csv_whole_list[:no_of_lines]
            for row in range(0, len(csv_list)):
                if row < 9:
                    dictOfWordsFromCSV[csv_list[row][0]] = [i for i in csv_list[row][1:] if i != '']
                    # complete list
                    dropdown_list.append([i for i in csv_list[row] if i != ''])
                elif row == 9:
                    continue
                else:
                    dropdown_list.append(csv_list[row])
            print('le')
            listOfWordsHeaders = csv_whole_list[10:12]
            if len(listOfWordsHeaders) > 0:
                for i in range(7):
                    dictOfWordsHeaders.append((i, listOfWordsHeaders[0][i], listOfWordsHeaders[1][i]))

        print(dictOfWordsHeaders)
        print(dropdown_list)

        # define columns for datas
        columns = ["Zeit", "Traversenweg", "Last", "Dehnung 1", "Dehn-ung 2", "Durchschnittliche Dehn-ung",
                   "Zugspannung"]
        preview_table = pd.DataFrame(csv_whole_list[12:22], columns=columns)
        return render_template('data.html', dropdown_list=dropdown_list, tables=[preview_table.to_html(classes='data')],
                               titles=columns)
        # return render_template('data.html', tables=[data_filtered[:no_of_lines].to_html(classes='data')],
        #                   titles=data_filtered.columns.values)# data=data_filtered[:no_of_lines].to_dict()


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    print(request.args.get('term'))
    # query = db_session.query(Movie.title).filter(Movie.title.like('%' + str(search) + '%'))
    # results = [mv[0] for mv in query.all()]
    print(str(search))
    results = class_labels  # ['Beer', 'Wine', 'Soda', 'Juice', 'Water']

    return jsonify(matching_results=results)


@app.route('/search', methods=['GET', 'POST'])  #
@returns_rdf
@custom_decorator
def search():
    # create graphs
    g_test = rdflib.Graph('IOMemory', rdflib.BNode())
    print('in search method ')
    class_labels = request.form.getlist('dropdown')
    print((class_labels))
    print(dictOfWordsFromCSV.get(class_labels[0]))
    gene = []
    for i in range(0, len(class_labels)):
        print(class_labels_dict.get(str(request.form.get("search" + str(i + 1)))))
        # gene.append((request.form.get("search" + str(i + 1)), class_labels[i]))
        # g.add((rdflib.URIRef(class_labels_dict.get(str(request.form.get("search" + str(i + 1))))),
        #       rdflib.Literal(class_labels[i]), rdflib.Literal(request.form.get("search" + str(i + 1)))))
        if i < 2:
            g_test.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasValue,
                        rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[0])))
            g_test.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasIdentifer,
                        rdflib.Literal(class_labels[i])))
        if i >= 2 and i < 9:
            g_test.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasValue,
                        rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[0])))
            g_test.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasUnit,
                        rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[1])))
            g_test.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasIdentifer,
                        rdflib.Literal(class_labels[i])))

    for j in range(7):
        g_test.add((rdflib.Literal('column ' + str(j)), OWL.hasLabel,
                    rdflib.Literal(dictOfWordsHeaders[j][1])))
        g_test.add((rdflib.Literal('column ' + str(j)), OWL.hasIndex,
                    rdflib.Literal(dictOfWordsHeaders[j][0])))
        g_test.add((rdflib.Literal('column ' + str(j)), OWL.hasUnit,
                    rdflib.Literal(dictOfWordsHeaders[j][2])))

    print('----------graph value----------------')
    # The turtle format has the purpose of being more readable for humans.
    print(g_test.serialize(format="turtle").decode())
    print(rdflib.Literal(request.form.get("search" + str(0))))
    # for s, p, o in g:
    #   print(s, p, o)
    gg = (request.form.get('search1'))
    # _Gene = request.form['inputGene']
    # _gene = str(gene)
    print('changed')
    # rint(gene, csv_values.get('prob'))
    selectValue = request.form.get('dropdown')
    ss = request.form.getlist('dropdown')
    print(ss)
    print(selectValue, gene)

    G = rdflib_to_networkx_multidigraph(g_test)
    # Plot Networkx instance of RDF Graph
    pos = nx.spring_layout(G, scale=2)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw(G, with_labels=True)
    plt.savefig('./rdf_triple.png')

    # save file as
    g_test.serialize("./test.ttl", format="turtle")
    # flash('RDF file successfully created')
    return g_test  # jsonify(g_test.serialize(format="turtle").decode())


@app.route('/showSelection', methods=['GET', 'POST'])
def showSelection():
    csv_values = {'prob': 21}
    gene = request.form.get('autocomplete')  # Returns none if not found in request
    gene = str(gene)
    print('change')
    print(gene, csv_values.get('prob'))
    flash('RDF file successfully created')
    return jsonify(gene, csv_values.get('prob'))


if __name__ == '__main__':
    app.run(debug=True)
