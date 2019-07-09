from django.shortcuts import render
from .models import proj_models, project, fields
import yaml
from django.http import JsonResponse

def get_models(request):
    data_type_choice = (
    ('str','string'),
    ('int','integer'),
    ('float','float'),
    ('date_time','date-time'),
    ('bool','boolean'),
    ('oto','one-to-one'),
    ('fkey','foreign_key'),
    ('mtm','many-to-many'),
)
    response = {}
    response['success'] = False
    response['message'] = 'No models available ...'
    dtype = {}
    for data_type in data_type_choice:
        dtype[data_type[0]] = data_type[1]

    proj = project.objects.get(name='proj1')
    models = proj.associated_models
    if len(models)>0:
        response['success'] = True
        response['message'] = 'Models Yaml generated succesfully'
    swagger = {}
    head = swagger
    swagger['definitions'] = {}
    swagger = swagger['definitions']
    rel_fields = {'oto','fkey','mtm'}
    for model in models:
    
        name = model.name
        swagger[name] = {}
        curr = swagger[name]
        curr['type'] = 'object'
        curr['xml'] = {}
        curr['xml']['name'] = name
        curr['properties']= {}
        fields = model.associated_fields
        curr = curr['properties']
        for f in fields:
            curr[f.name] = {}
            curr = curr[f.name]
            if f.data_type not in rel_fields:
                curr['type'] = dtype[f.data_type]
            else:
                rel_model = f.related_model.name   
                curr['$ref'] = '#/definitions/'+str(rel_model)

    
    yaml.dump(head, open("models.yaml", "w"))
    print(yaml.dump(head))
    return JsonResponse(response)

def generate_output_yaml(request):
    open('swagger_final.yaml','w').close()
    op_file = open('swagger_final.yaml','a')
    file_list = ['swagger_base.yaml','models.yaml']
    for file in file_list:
        curr_file = open(file,'r')
        op_file.write(curr_file.read())
        curr_file.close
        op_file.write('\n')
    op_file.close
    response = {}
    response['success'] = True
    response['message'] = 'Doc Yaml generated succesfully'

    return JsonResponse(response)