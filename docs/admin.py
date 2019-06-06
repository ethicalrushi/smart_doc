from django.contrib import admin
from .models import fields, developer, project, proj_models
# Register your models here.

class dev_Admin(admin.ModelAdmin):  
    def get_dev_projects(self,object):
        return ", ".join([p.name for p in object.dev_project.all()])

    get_dev_projects.short_description = 'projects'
    list_display =['user','get_dev_projects','status','created','modified'] #Listing many to mamny field using method

class model_Admin(admin.ModelAdmin):
	list_display=['name','project','registered','created','modified']

class proj_Admin(admin.ModelAdmin):
	list_display=['name','registered','created','modified']

class fields_Admin(admin.ModelAdmin):
	list_display=['name','data_type','field_type','related_model','model','created','modified']

admin.site.register(developer,dev_Admin)
admin.site.register(proj_models,model_Admin)
admin.site.register(project,proj_Admin)
admin.site.register(fields,fields_Admin)