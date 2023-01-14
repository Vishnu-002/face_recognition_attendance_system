import django_filters
from django_filters import DateFilter
from .models import Attendence

class AttendenceFilter(django_filters.FilterSet):
    # dates = DateFilter(field_name="date")
    class Meta:
        model = Attendence
        fields = '__all__'
        exclude = ['Faculty_Name', 'status','time','year']