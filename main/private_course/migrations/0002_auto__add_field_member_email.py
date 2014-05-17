# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Member.email'
        db.add_column('private_course_member', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Member.email'
        db.delete_column('private_course_member', 'email')


    models = {
        'private_course.member': {
            'Meta': {'object_name': 'Member'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'members'", 'symmetrical': 'False', 'through': "orm['private_course.Membership']", 'to': "orm['private_course.PrivateCourse']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'dob': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'skype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'specialization': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'private_course.membership': {
            'Meta': {'object_name': 'Membership'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['private_course.PrivateCourse']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['private_course.Member']"})
        },
        'private_course.privatecourse': {
            'Meta': {'ordering': "['position']", 'object_name': 'PrivateCourse'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'hours': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['private_course']