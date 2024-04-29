import datetime
import uuid
from django.apps import apps as django_apps
from django.db.models import ManyToManyField, ForeignKey, OneToOneField, ManyToOneRel
from django.db.models.fields.reverse_related import OneToOneRel
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import xlwt


class ExportActionMixin:
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % (
            self.get_export_filename())

        wb = xlwt.Workbook(encoding='utf-8', style_compression=2)
        ws = wb.add_sheet('%s')

        row_num = 0
        obj_count = 0
        self.inline_header = False

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.num_format_str = 'YYYY/MM/DD h:mm:ss'

        field_names = []
        for field in self.get_model_fields:
            if isinstance(field, ManyToManyField):
                choices = self.m2m_list_data(field.related_model)
                for choice in choices:
                    field_names.append(choice)
                continue
            field_names.append(field.name)

        if queryset and getattr(queryset[0], 'facet_visit', None):
            field_names.insert(0, 'subject_identifier')
            field_names.insert(1, 'visit_code')

        if self.is_consent(queryset[0]):
            field_names.append("mother_hiv_status")
            field_names.append("consent_child_age_in_months")
            field_names.append("current_child_age_in_months")

        for col_num in range(len(field_names)):
            ws.write(row_num, col_num, field_names[col_num], font_style)

        for obj in queryset:
            data = []
            inline_field_names = []

            # Add subject identifier and visit code
            if getattr(obj, 'facet_visit', None):

                subject_identifier = obj.facet_visit.subject_identifier

                data.append(subject_identifier)
                data.append(obj.facet_visit.visit_code)

            inline_objs = []

            for field in self.get_model_fields:

                if isinstance(field, ManyToManyField):
                    m2m_values = self.get_m2m_values(obj, m2m_field=field)
                    data.extend(m2m_values)
                    continue
                if isinstance(field, (ForeignKey, OneToOneField,)):
                    field_value = getattr(obj, field.name)
                    data.append(field_value.id)
                    continue
                if isinstance(field, OneToOneRel):
                    continue
                if not self.is_consent(obj) and isinstance(field, ManyToOneRel):
                    key_manager = getattr(obj, f'{field.name}_set')
                    inline_values = key_manager.all()
                    fields = field.related_model._meta.get_fields()
                    for field in fields:
                        if not isinstance(field,
                                          (ForeignKey, OneToOneField, ManyToManyField,)):
                            inline_field_names.append(field.name)
                        if isinstance(field, ManyToManyField):
                            choices = self.m2m_list_data(field.related_model)
                            inline_field_names.extend(
                                [choice for choice in choices])
                    if inline_values:
                        inline_objs.append(inline_values)
                field_value = getattr(obj, field.name, '')
                data.append(field_value)

            if self.is_consent(obj):
                data.append(obj.hiv_status)
                data.append(obj.consent_child_age)
                data.append(obj.current_child_age)

            if not self.is_consent(obj) and inline_objs:
                # Update header
                inline_field_names = self.inline_exclude(
                    field_names=inline_field_names)
                if not self.inline_header:
                    self.update_headers_inline(
                        inline_fields=inline_field_names, field_names=field_names,
                        ws=ws, row_num=0, font_style=font_style)

                for inline_qs in inline_objs:
                    for inline_obj in inline_qs:
                        inline_data = []
                        inline_data.extend(data)
                        for field in inline_obj._meta.get_fields():
                            if field.name in inline_field_names:
                                inline_data.append(
                                    getattr(inline_obj, field.name, ''))
                            if isinstance(field, ManyToManyField):
                                m2m_values = self.get_m2m_values(inline_obj,
                                                                 m2m_field=field)
                                inline_data.extend(m2m_values)
                        row_num += 1
                        self.write_rows(data=inline_data,
                                        row_num=row_num, ws=ws)
                obj_count += 1
            else:
                row_num += 1

                self.write_rows(data=data, row_num=row_num, ws=ws)
        wb.save(response)
        return response

    export_as_csv.short_description = _(
        'Export selected %(verbose_name_plural)s')

    actions = [export_as_csv]

    def write_rows(self, data=None, row_num=None, ws=None):

        for col_num in range(len(data)):
            if isinstance(data[col_num], uuid.UUID):
                ws.write(row_num, col_num, str(data[col_num]))
            elif isinstance(data[col_num], datetime.datetime):
                dt = data[col_num]
                if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
                    dt = timezone.make_naive(dt)
                dt = dt.strftime('%Y/%m/%d')
                ws.write(row_num, col_num, dt, xlwt.easyxf(
                    num_format_str='YYYY/MM/DD'))
            elif isinstance(data[col_num], datetime.date):
                ws.write(row_num, col_num, data[col_num], xlwt.easyxf(
                    num_format_str='YYYY/MM/DD'))
            else:
                ws.write(row_num, col_num, data[col_num])

    def update_headers_inline(self, inline_fields=None, field_names=None,
                              ws=None, row_num=None, font_style=None):
        top_num = len(field_names)
        for col_num in range(len(inline_fields)):
            ws.write(row_num, top_num, inline_fields[col_num], font_style)
            top_num += 1
            self.inline_header = True

    def get_export_filename(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = "%s-%s" % (self.model.__name__, date_str)
        return filename

    def screening_identifier(self, subject_identifier=None):
        """Returns a screening identifier.
        """
        consent = self.consent_obj(subject_identifier=subject_identifier)

        if consent:
            return getattr(consent, 'screening_identifier', None)
        return None

    def consent_obj(self, subject_identifier: str):
        consent_cls = django_apps.get_model('flourish_facet.facetconsent')
        consent = consent_cls.objects.filter(
            subject_identifier=subject_identifier)

        if consent.exists():
            return consent.last()
        return None

    def is_consent(self, obj):
        consent_cls = django_apps.get_model('flourish_facet.facetconsent')
        return isinstance(obj, consent_cls)

    def is_visit(self, obj):
        visit_cls = django_apps.get_model('flourish_facet.facetvisit')
        return isinstance(obj, visit_cls)

    @property
    def get_model_fields(self):
        return [field for field in self.model._meta.get_fields()
                if field.name not in self.exclude_fields and not isinstance(field,
                                                                            OneToOneRel)]

    def inline_exclude(self, field_names=[]):
        return [field_name for field_name in field_names
                if field_name not in self.exclude_fields]

    @property
    def exclude_fields(self):
        return ['created', '_state', 'hostname_created', 'hostname_modified',
                'revision', 'device_created', 'device_modified', 'id', 'site_id',
                'created_time', 'modified_time', 'report_datetime_time',
                'registration_datetime_time', 'screening_datetime_time', 'modified',
                'form_as_json', 'consent_model', 'randomization_datetime',
                'registration_datetime', 'is_verified_datetime', 'first_name',
                'last_name', 'initials', 'identity', 'facet_visit_id', 'confirm_identity',
                'motherchildconsent', ]

    def m2m_list_data(self, model_cls=None):
        qs = model_cls.objects.order_by(
            'created').values_list('short_name', flat=True)
        return list(qs)

    def get_m2m_values(self, model_obj, m2m_field=None):
        m2m_values = []
        model_cls = m2m_field.related_model
        choices = self.m2m_list_data(model_cls=model_cls)
        key_manager = getattr(model_obj, m2m_field.name)
        for choice in choices:
            selected = 0
            try:
                key_manager.get(short_name=choice)
            except model_cls.DoesNotExist:
                pass
            else:
                selected = 1
            m2m_values.append(selected)
        return m2m_values
