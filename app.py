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
import document
from rdflib import ConjunctiveGraph, URIRef, RDFS, Literal
from flask_table import Table, Col
from flask import send_file
from rdflib.namespace import RDF, XSD, NamespaceManager
from rdflib import BNode, Literal, Namespace, Graph
from wtforms import TextField, Form
from fast_autocomplete import AutoComplete

from collections import defaultdict
import io
import re


def regex(str):
    # use regex to split
    test = "".join(re.split("[^a-z A-Z 0-9 -|,| ()| .| ;| ^/ ^%]*", str)).split(' ')

    return [i for i in test if i != ""]


app = Flask(__name__)
# app env list
app.jinja_env.filters['regex'] = regex

## app.secret_key = b'_5#y2L"F4Q8z\n\xec]/''

# autocomplete dict
autocmplete_label_dict = {}

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
        autocmplete_label_dict[result.label(s).title()] = {}
        final_list.append((s.title(), result.label(s).title()))
        class_labels_dict[result.label(s).title()] = s.title()
    labels = list(set([i for i in final_list if len(i[1]) > 0]))
    print(len(labels))
    # print(class_labels_dict)
    print(class_labels_dict.get('Computertomograph'))
    # print(class_labels_dict.get('DepthOfCut'))
    rdf_df = pd.DataFrame(labels, columns=['class(subject)', 'label(literals)'])
    alert_value = 1  # for alert.
    return render_template('turtle_list.html', tables=[rdf_df.to_html(classes='data')], titles=rdf_df.columns.values)
    # render_template('index_old.html', alert_value=alert_value)


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
    :return: data in CSV file..
    """
    # counter_first_null = 0
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
            # csv_list = csv_whole_list[:no_of_lines]
            for row in range(0, len(csv_whole_list)):
                print(row)
                # counter_first_null += 1
                if csv_whole_list[row][0] == '':
                    print(row)
                    break
                else:
                    if row < no_of_lines:
                        dictOfWordsFromCSV[csv_whole_list[row][0]] = [i for i in csv_whole_list[row][1:] if i != '']
                        # complete list
                        dropdown_list.append([i for i in csv_whole_list[row] if i != ''])
                # if row[0] != '':  # < 9
                #     dictOfWordsFromCSV[csv_list[row][0]] = [i for i in csv_list[row][1:] if i != '']
                #     # complete list
                #     dropdown_list.append([i for i in csv_list[row] if i != ''])
                # elif row == 9:
                #     continue
                # else:
                #     dropdown_list.append(csv_list[row])
            print('you are in data ')
            listOfWordsHeaders = csv_whole_list[row + 1:row + 3]  # 10:12
            if len(listOfWordsHeaders) > 0:
                for i in range(7):
                    dictOfWordsHeaders.append((i, listOfWordsHeaders[0][i], listOfWordsHeaders[1][i]))

        print(dictOfWordsHeaders)
        print(dropdown_list)

        # define columns for datas
        columns = ["Zeit", "Traversenweg", "Last", "Dehnung 1", "Dehn-ung 2", "Durchschnittliche Dehn-ung",
                   "Zugspannung"]
        preview_table = pd.DataFrame(csv_whole_list[row + 3:22], columns=columns)
        return render_template('data.html', dropdown_list=dropdown_list, tables=[preview_table.to_html(classes='data')],
                               titles=columns)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    print(request.args.get('term'))
    print('search is ---------')
    print(str(search))
    autocomplete = AutoComplete(words=autocmplete_label_dict)
    print(autocomplete.search(word=str(search), max_cost=3, size=3))
    t = autocomplete.search(word=str(search), max_cost=3, size=6)

    flatten = [item for sublist in t for item in sublist]
    print(flatten)

    # results = autocomplete.search(word=str(search), max_cost=3, size=3) #class_labels  # ['Beer', 'Wine', 'Soda', 'Juice', 'Water']
    results = flatten
    print(results)

    return jsonify(matching_results=results)


@app.route('/search', methods=['GET', 'POST'])  #
@returns_rdf
@custom_decorator
def search():
    # test namespace
    BS = rdflib.Namespace('https://w3id.org/def/basicsemantics-owl#')
    # test graph
    csv_test_graph = rdflib.Graph('IOMemory', rdflib.BNode())
    # create graph
    csv_graph = rdflib.Graph('IOMemory', rdflib.BNode())
    print(request.data)
    print('in search method ---')
    print(str(request.form.get("searchx1")))
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
            csv_graph.add(
                (rdflib.Literal(request.form.get("search" + str(i + 1))), BS[request.form.get("prop" + str(i + 1))],
                 rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[0])))
            csv_graph.add(
                (rdflib.Literal(request.form.get("search" + str(i + 1))), BS[request.form.get("prop" + str(i + 1))],
                 rdflib.Literal(class_labels[i])))
        if i >= 2 and i < 9:
            csv_graph.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasValue,
                           rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[0])))
            csv_graph.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasUnit,
                           rdflib.Literal(dictOfWordsFromCSV.get(class_labels[i])[1])))
            csv_graph.add((rdflib.Literal(request.form.get("search" + str(i + 1))), OWL.hasIdentifier,
                           rdflib.Literal(class_labels[i])))
        # owl = OWL.str(request.form.get("prop1"))

        # test graph add data request.form.get("search" + str(i + 1))
        # csv_test_graph.add((rdflib.URIRef(request.form.get("search" + str(i + 1))),
        #                     BS[request.form.get("prop" + str(i + 1))],
        #                     rdflib.Literal(request.form.get("searchx" + str(
        #                         i + 1)))))  # rdflib.RDF.type(str(request.form.get("prop" + str(i + 1))))

    for j in range(7):
        csv_graph.add((rdflib.Literal('column ' + str(j)), OWL.hasLabel,
                       rdflib.Literal(dictOfWordsHeaders[j][1])))
        csv_graph.add((rdflib.Literal('column ' + str(j)), OWL.hasIndex,
                       rdflib.Literal(dictOfWordsHeaders[j][0])))
        csv_graph.add((rdflib.Literal('column ' + str(j)), OWL.hasUnit,
                       rdflib.Literal(dictOfWordsHeaders[j][2])))

    print('----------graph value----------------')
    print(csv_test_graph.serialize(format="turtle").decode())
    # The turtle format has the purpose of being more readable for humans.
    print(csv_graph.serialize(format="turtle").decode())
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

    G = rdflib_to_networkx_multidigraph(csv_graph)
    # Plot Networkx instance of RDF Graph
    pos = nx.spring_layout(G, scale=2)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw(G, with_labels=True)
    plt.savefig('./rdf_triple.png')

    # save file
    csv_graph.serialize("./test.ttl", format="turtle")
    # flash('RDF file successfully created')
    return csv_graph  # jsonify(g_test.serialize(format="turtle").decode())


@app.route('/showSelection', methods=['GET', 'POST'])
@returns_rdf
@custom_decorator
def showSelection():
    # flash('RDF file successfully created')
    BMWD = Namespace('https://www.materials.fraunhofer.de/ontologies/BWMD_ontology/mid#')
    UNIT = Namespace('http://qudt.org/2.1/vocab/unit/')
    BS = Namespace('https://w3id.org/def/basicsemantics-owl#')

    g = Graph()
    g.namespace_manager = NamespaceManager(Graph())
    g.namespace_manager.bind('unit', UNIT)
    g.namespace_manager.bind('bs', BS)
    g.namespace_manager.bind('bmwd', BMWD)

    print('in showSelection method changed---')
    print(request.form.getlist('dropdown'))
    print(str(request.form.get("search1")))
    # test=request.form.get('dropdown1')
    for i in range(0, 30):
        test = request.form.get('dropdown' + str(i))
        if test:
            # filter_data = re.split("\s\s|;|\t", test)
            filter_data = [i for i in re.split("\s\s|;|\t", test) if i != '']
            print(filter_data)
            if len(filter_data) <= 2:
                g.add((Literal(request.form.get("search" + str(i))), BS['hasValue'], Literal(filter_data[-1])))
            else:
                if re.findall('[0-9]+', filter_data[1]):
                    g.add((BMWD[request.form.get("search" + str(i))], UNIT['hasUnit'], Literal(filter_data[2])))
                    g.add((BMWD[request.form.get("search" + str(i))], BS['hasValue'], Literal(filter_data[1])))
                else:
                    g.add((BMWD[request.form.get("search" + str(i))], BS['hasValue'], Literal(filter_data[2])))
                    g.add((BMWD[request.form.get("search" + str(i))], UNIT['hasUnit'], Literal(filter_data[1])))

            # print(len([i for i in b if i != '']))
            print(str(request.form.get("search" + str(i))))

    return g


@app.route('/test_read', methods=['GET', 'POST'])
def test_read():
    # file to reads
    file = request.form['upload-file']
    no_of_lines = int(request.form['no_of_rows_csv'])
    print(no_of_lines)
    file_data = []
    with open(file) as f:
        d = defaultdict(list)
        for line in f:
            file_data.append(line)
    # some thing
    return render_template('regex_file.html', data=file_data[:30])


if __name__ == '__main__':
    app.run(debug=True)
