import locale
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from fast_autocomplete import AutoComplete
from django.http import JsonResponse
import rdflib
import pandas as pd
import re
import chardet

import rdflib
import pandas as pd
from flask_rdf.bottle import returns_rdf
from rdflib.namespace import RDF, XSD, NamespaceManager
from rdflib import BNode, Literal, Namespace, Graph
import flask_rdf
import csv
import os
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

# autocomplete dict
autocmplete_label_dict = {}
class_labels = []
class_labels_dict = {}
dictOfWordsFromCSV = {}
dictOfWordsHeaders = []
listOfWordsHeaders = []
# set up a custom formatter to return turtle in text/plain to browsers
custom_formatter = flask_rdf.FormatSelector()
custom_formatter.wildcard_mimetype = 'text/plain'
custom_formatter.add_format('text/plain', 'turtle')
custom_decorator = flask_rdf.flask.Decorator(custom_formatter)

# define graph
g = rdflib.Graph()


def regex(str):
    # use regex to split
    test = " ".join(re.split("\s\s|;|\t", str)).split(' ')
    # test = "".join(re.split("[^a-z A-Z 0-9  - |,| pow|()| .| ;| ^/ ^%]*", str)).split(' ')
    # [i for i in re.split("\s\s|;|\t", test) if i != '']

    return [i for i in test if i != ""]


# Create your views here.
def homepage(request):
    return HttpResponse("this is test appplication.")


def hello_world(request):
    return render(request, 'hello_world.html', {})


def read_file(request):
    """
    This is first landing page.
    :return:
    """
    return render(request, 'index.html', {})


@csrf_exempt
def parse_data(request):
    f = request.FILES['file']
    print("file is ", f.file)
    print("---------------------------------")
    print(type(request.POST['no_of_rows_csv']))
    my_file = f.file
    print(my_file)
    file_data = []
    while True:
        line = my_file.readline()
        # print(line.decode('ISO-8859-1'))
        # file_data.append(line.decode('ISO-8859-1'))
        filtered_data = regex(line.decode('ISO-8859-1'))
        if len(filtered_data) > 0:
            # filter_data = [i for i in re.split("\s\s|;|\t", tt) if i != '']
            # print("".join([i for i in filtered_data]))
            file_data.append(" ".join([i for i in filtered_data]))
        # print(chardet.detect(line))
        # print(line.decode('ISO-8859-1'))
        if not line:
            break
    return render(request, 'regex_file.html', {"file_data": file_data[:int(request.POST['no_of_rows_csv'])]})


@csrf_exempt
def autocomplete(request):
    """
    This is autocomplete method.
    :return:
    """
    search = request.GET.get('q')
    # print(request.GET.get('term'))
    print('search is -----------')
    print(str(search))
    auto_complete = AutoComplete(words=autocmplete_label_dict)
    print(auto_complete.search(word=str(search), max_cost=3, size=3))
    t = auto_complete.search(word=str(search), max_cost=3, size=6)
    flatten = [item for sublist in t for item in sublist]
    print(flatten)
    results = flatten
    print(results)

    return JsonResponse({'matching_results': results})


@csrf_exempt
def read_turte(request):
    """
    Read the turtle file
    :return: turtle class and literals.
    """
    file = request.FILES['file']
    print(file)
    # no_of_rows = int(request.form['no_of_rows'])
    owlClass = rdflib.namespace.OWL.Class
    rdfType = rdflib.namespace.RDF.type

    result = g.parse(file, format="turtle")
    final_list = []
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
    return render(request, 'index.html')
    # render('turtle_list.html', {'tables': [rdf_df.to_html(classes='data')], 'titles': rdf_df.columns.values})
    # render_template('index_old.html', alert_value=alert_value)


@csrf_exempt
def selection(request):
    print("----------Show----------------")
    # input1= request.GET.get('obj')
    # print(input1)
    BMWD = Namespace('https://www.materials.fraunhofer.de/ontologies/BWMD_ontology/mid#')
    UNIT = Namespace(
        'http://www.ontologyrepository.com/CommonCoreOntologies/Mid/InformationEntityOntology')  # http://www.qudt.org/2.1/vocab/unit
    BS = Namespace('https://w3id.org/def/basicsemantics-owl#')

    g = Graph()
    g.namespace_manager = NamespaceManager(Graph())
    g.namespace_manager.bind('unit', UNIT)
    g.namespace_manager.bind('bs', BS)
    g.namespace_manager.bind('bmwd', BMWD)
    subjects = request.POST['test1']
    print(subjects)
    objects = request.POST['test2'].split(",")
    print(objects)
    # test = "/".join(re.split("\s\s|;|\t", subjects)).split("/")
    test = subjects.split(";")
    for i in range(len(test)):
        if (len(test[i]) > 0 and test[i][0] == ","):
            test[i] = test[i][1:]
        filter_data = test[i].split(" ")
        print("data is ", filter_data)
        # print("filter_data is ",filter_data)
        if len(filter_data) > 0 and len(filter_data[0])>0:
            if len(filter_data) <= 2:
                print(filter_data)
                g.add((BMWD[objects[i]], BS['hasValue'], Literal(filter_data[-1])))
            else:
                if re.findall('[0-9]+', filter_data[1]):
                    g.add((BMWD[objects[i]], UNIT['hasUnit'], Literal(filter_data[2])))
                    g.add((BMWD[objects[i]], BS['hasValue'], Literal(filter_data[1])))
                else:
                    g.add((BMWD[objects[i]], BS['hasValue'], Literal(filter_data[2])))
                    g.add((BMWD[objects[i]], UNIT['hasUnit'], Literal(filter_data[1])))

            # print(len([i for i in b if i != '']))
    print(g.serialize(format="turtle").decode())
    results= g.serialize(format="turtle").decode()
    return  render(request, 'graph.html', {'results': results})
        #JsonResponse({'matching_results': g.serialize(format="turtle").decode()})
