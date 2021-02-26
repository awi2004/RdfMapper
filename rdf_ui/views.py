import locale
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from fast_autocomplete import AutoComplete
from django.http import JsonResponse
import rdflib
import pandas as pd
import chardet

# autocomplete dict
autocmplete_label_dict = {}
class_labels = []
class_labels_dict = {}
dictOfWordsFromCSV = {}
dictOfWordsHeaders = []
listOfWordsHeaders = []

# define graph
g = rdflib.Graph()


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
    # print("file is ", f.file)
    print("---------------------------------")
    print(type(request.POST['no_of_rows_csv']))
    my_file = f.file
    file_data = []
    while True:
        line = my_file.readline()
        file_data.append(line.decode('ISO-8859-1'))
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
    #print(request.GET.get('term'))
    print('search is -----------')
    print(str(search))
    auto_complete = AutoComplete(words=autocmplete_label_dict)
    print(auto_complete.search(word=str(search), max_cost=3, size=3))
    t = auto_complete.search(word=str(search), max_cost=3, size=6)
    flatten = [item for sublist in t for item in sublist]
    print(flatten)
    results = flatten
    print(results)

    return JsonResponse({'matching_results':results})


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
    return render(request,'index.html')
    #render('turtle_list.html', {'tables': [rdf_df.to_html(classes='data')], 'titles': rdf_df.columns.values})
    # render_template('index_old.html', alert_value=alert_value)
