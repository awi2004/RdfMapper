from flask import Flask, render_template, request, Response
import json
import rdflib
from flask import jsonify
import pandas as pd
from rdflib import ConjunctiveGraph, URIRef, RDFS, Literal
from flask_table import Table, Col
from wtforms import TextField, Form

app = Flask(__name__)

class_labels = []


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
    no_of_rows = int(request.form['no_of_rows'])
    g = rdflib.Graph()
    # g = ConjunctiveGraph()
    owlClass = rdflib.namespace.OWL.Class
    rdfType = rdflib.namespace.RDF.type

    result = g.parse(file, format="turtle")
    final_list = []
    # Iterate over triples in store and print them out.
    # for s, p, o in result:
    #     # if type(o) == rdflib.term.Literal:
    #     # sub.append(s),prop.append(p),obj.append(o)
    #     # final_list.append((s, o))
    #     final_list.append((s, g.label(s)))
    for s in result.subjects(predicate=rdfType, object=owlClass):
        class_labels.append(result.label(s))
        final_list.append((s, result.label(s)))
    labels = list(set([i for i in final_list if len(i[1]) > 0]))
    print(len(labels))
    rdf_df = pd.DataFrame(labels, columns=['class(subject)', 'label(literals)'])

    return render_template('turtle_list.html', tables=[rdf_df[:no_of_rows].to_html(classes='data')],
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
    if request.method == 'POST':
        file = request.form['upload-file']
        no_of_lines = int(request.form['no_of_rows_csv'])
        # print(file)
        # final_list= read_turte()
        data = pd.read_csv(file, sep=";", index_col=None, encoding="ISO-8859-1")
        data_filtered = pd.DataFrame(data)
        # data = pd.read_excel(open('tmp.xlsx', 'rb'))
        print('data is')
        dropdown_list = data_filtered.columns
        return render_template('data.html', dropdown_list=dropdown_list)
        #return render_template('data.html', tables=[data_filtered[:no_of_lines].to_html(classes='data')],
        #                   titles=data_filtered.columns.values)# data=data_filtered[:no_of_lines].to_dict()


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    # query = db_session.query(Movie.title).filter(Movie.title.like('%' + str(search) + '%'))
    # results = [mv[0] for mv in query.all()]
    print(str(search))
    results = class_labels  # ['Beer', 'Wine', 'Soda', 'Juice', 'Water']

    return jsonify(matching_results=results)


@app.route('/search', methods=['GET', 'POST'])
def search():
    csv_values = {'prob': 21}
    # form = SearchForm(request.form)
    # print('from search is')
    # form['autocomplete']
    # print(form['autocomplete'])
    print('in search method is tell ')
    gene = request.form.get('autocomplete')
    # _Gene = request.form['inputGene']
    _gene = str(gene)
    print('changessd')
    print(gene, csv_values.get('prob'))
    selectValue = request.form.get('dropdown')
    print(selectValue)
    return jsonify(gene, selectValue)


@app.route('/showSelection', methods=['GET', 'POST'])
def showSelection():
    csv_values = {'prob': 21}
    gene = request.form.get('autocomplete')  # Returns none if not found in request
    gene = str(gene)
    print('changess')
    print(gene, csv_values.get('prob'))
    return jsonify(gene, csv_values.get('prob'))


if __name__ == '__main__':
    app.run(debug=True)
