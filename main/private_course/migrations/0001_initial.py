# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PrivateCourse'
        db.create_table('private_course_privatecourse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('hours', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('private_course', ['PrivateCourse'])

        # Adding model 'Membership'
        db.create_table('private_course_membership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['private_course.Member'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['private_course.PrivateCourse'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('private_course', ['Membership'])

        # Adding model 'Member'
        db.create_table('private_course_member', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('dob', self.gf('django.db.models.fields.DateField')()),
            ('skype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('specialization', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('private_course', ['Member'])


    def backwards(self, orm):
        # Deleting model 'PrivateCourse'
        db.delete_table('private_course_privatecourse')

        # Deleting model 'Membership'
        db.delete_table('private_course_membership')

        # Deleting model 'Member'
        db.delete_table('private_course_member')


    models = {
        'private_course.member': {
            'Meta': {'object_name': 'Member'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'members'", 'symmetrical': 'False', 'through': "orm['private_course.Membership']", 'to': "orm['private_course.PrivateCourse']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'dob': ('django.db.models.fields.DateField', [], {}),
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