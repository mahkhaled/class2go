from django.shortcuts import get_object_or_404

from django.core.urlresolvers import reverse_lazy

from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from .models import PrivateCourse
from .models import Member
from .forms import MemberForm

class PrivateCourseDetailView(DetailView):
  model = PrivateCourse
  

class PrivateCourseListView(ListView):
  model = PrivateCourse
  queryset = PrivateCourse.objects.filter(active=True)

  def get_context_data(self, **kwargs):
    context = super(PrivateCourseListView, self).get_context_data(**kwargs)
    context['category'] = self.request.GET.get('category', '0')
    return context

class MemberCreateView(CreateView):
  model = Member
  form_class = MemberForm
  success_url = reverse_lazy('private_course_list')

  def get_context_data(self, **kwargs):
    context = super(MemberCreateView, self).get_context_data(**kwargs)
    context['category'] = self.request.GET.get('category', '0')
    return context

  def get(self, request, *args, **kwargs):
    get_object_or_404(PrivateCourse, pk=kwargs['course_id'])
    return super(MemberCreateView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    course = get_object_or_404(PrivateCourse, pk=kwargs['course_id'])
    category = self.request.POST.get('category', '0')
    form_class = self.get_form_class()
    form = form_class(self.request.POST, None)
    
    if form.is_valid():
      member = form.save()
      member.create_membership(course=course, category=category)
      return self.form_valid(form)
    else:
      self.object = form.instance
      return self.form_invalid(form)