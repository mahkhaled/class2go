from django.db import models

# Create your models here.

PAYMENTS = (('1', '2'),)
CATEGORIES = (
  ('0', 'Individual'),
  ('1', 'Group'),
)

SPECIALIZATION = (('a', 'a'),)


class PrivateCourse(models.Model):
  title = models.CharField('Title', max_length=255)
  description = models.TextField('Description')
  position = models.IntegerField('Position')
  active = models.BooleanField('Active')
  capacity = models.IntegerField('Capacity')
  hours = models.IntegerField('Hours')


  def is_full(self):
    return self.capacity <= self.members.count()

  def remaining(self):
    try:
      return self.capacity - self.members.count()
    except:
      return 0

  def __unicode__(self):
    return self.title

  class Meta:
    ordering = ['position']
    verbose_name = 'Private Course'
    verbose_name_plural = 'Private Courses'

class Membership(models.Model):
  member = models.ForeignKey('Member')
  course = models.ForeignKey(PrivateCourse)
  category = models.CharField('Category', max_length=255, choices=CATEGORIES)
  # unique_together = ('member', 'course')

  def __unicode__(self):
    return " >> ".join([self.member.name, self.course.title])
  
class Member(models.Model):
  name = models.CharField('Name', max_length=255)
  email = models.EmailField('Email', max_length=255)
  country = models.CharField('Country', max_length=255)
  description = models.TextField('You need a private lesson about:')
  dob = models.DateField('Date of Birth')
  skype = models.CharField('Skype', max_length=255)
  specialization = models.CharField('Specialization', max_length=255, choices=SPECIALIZATION)
  payment = models.CharField('Payment', max_length=255, choices=PAYMENTS)
  courses = models.ManyToManyField(PrivateCourse, through='Membership', related_name='members')

  def __unicode__(self):
    return self.name

  def create_membership(self, course, category):
    return Membership.objects.create(member=self, course=course, category=category)
