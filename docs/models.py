from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
import datetime

class fields(models.Model):
    """
    Defines fields to either attach with a model or keep it generic to use in a model afterwards

    Keeping the fields on associated_model deletion since we want to have generic_fields preserved.
    Restrict deletion of associated_models from fields for model_fields or make them generic if deletion is forced.
    """

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

    field_association_choice = (
        ('gen','generic'),
        ('mod','model_field'),
    )

    name = models.CharField(max_length=100, null=False, blank=False)
    data_type = models.CharField(max_length=9, choices= data_type_choice, 
                                default = 'str', null=False, blank=False)
    field_type = models.CharField(max_length=3, choices= field_association_choice,
                                default='mod')
    related_model = models.ForeignKey('proj_models', on_delete=models.CASCADE, related_name='related_model', null=True, blank=True) 
    model = models.ForeignKey('proj_models', related_name='fields', null=True, blank=True, on_delete=models.PROTECT)
    associated_developer = models.OneToOneField('developer',null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        d_type = self.data_type
        data_type_ref_set = {'fkey','oto','mtm'}
        related_model_value = self.related_model
        if str(d_type) in data_type_ref_set and related_model_value is None:
            raise ValidationError(
                _('You must have a related model linked to this field'),
                params={'value': related_model_value},
            )
        if str(self.field_type)=='gen' and self.associated_developer is None:
            raise ValidationError(
                _('You must have a developer associated for generic fields'),
                params={'value': self.associated_developer},
            )
        else:
            if str(self.field_type)=='mod' and self.model is None:
                raise ValidationError(
                    _('You must have an associated model for model fields'),
                    params={'value':self.model},
                )
    def __str__(self):
        return self.name

class proj_models(models.Model):
    """
    Model for project_model either associated with project or generic

    registered- if true the project can generate doc and must have some model associated,
                till then project is assumed to be in development stage and can have no models
    """

    model_association_choice = (
        ('gen','generic'),
        ('mod','project_model'),
    )
    name = models.CharField(max_length=100, null=False, blank=False)
    model_type = models.CharField(max_length=3, choices=model_association_choice,
                                default='mod')
    project = models.ForeignKey('project', related_name='project_models', null=True, blank=True, on_delete=models.PROTECT)
    associated_developer = models.OneToOneField('developer',null=True, blank=True, on_delete=models.CASCADE)
    registered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    @property
    def associated_fields(self):
        return self.fields.all()

    def clean(self):
        value = self.associated_fields.count()
        if  self.registered==True and value==0:
            raise ValidationError(
                _('You must add some fields to the model before registering it.'),
                params={'value':value},
            )
        if str(self.model_type)=='gen' and self.associated_developer is None:
            raise ValidationError(
                _('You must have a developer associated for generic models'),
                params={'value': self.associated_developer},
            )
        else:
            if str(self.model_type)=='mod' and self.project is None:
                raise ValidationError(
                _('You must have a project associated for project models'),
                params={'value': self.project},
            )
            
    def __str__(self):
        return self.name

class project(models.Model):
    """
    Model for a project associated with developer

    registered- if true the project can generate doc and must have some model associated,
                till then project is assumed to be in development stage and can have no models
    """

    name = models.CharField(max_length=150, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    registered = models.BooleanField(default=False)

    @property
    def associated_models(self):
        return self.project_models.all()

    def clean(self):
        value = self.associated_models.count()
        if  self.registered==True and value==0:
            raise ValidationError(
                _('You must add some models to the project before registering it.'),
                params={'value':value},
            )

    def __str__(self):
        return self.name

class developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dev_project = models.ManyToManyField(project, blank=True)
    github = models.URLField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    status = models.BooleanField(default=False)

    def get_dev_projects(self):
        return ",".join([p.name for p in self.dev_project.all()])

    def __str__(self):
        return str(self.user)