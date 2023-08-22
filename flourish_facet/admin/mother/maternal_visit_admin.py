from django.contrib import admin
from ...models import MaternalVisit
from ...forms import MaternalVisitForm
from ...admin_site import flourish_facet_admin
from edc_model_admin import audit_fieldset_tuple
from edc_visit_schedule.fieldsets import visit_schedule_fieldset_tuple
from edc_visit_tracking.modeladmin_mixins import VisitModelAdminMixin


@admin.register(MaternalVisit, site=flourish_facet_admin)
class MaternalVisitAdmin(VisitModelAdminMixin, admin.ModelAdmin):
    form = MaternalVisitForm

    fieldsets = (
        (None, {
            'fields': [
                'appointment',
                'report_datetime',
                'reason',
                'reason_missed',
                'study_status',
                'info_source',
                'info_source_other',
                'is_present',
                'survival_status',
                'last_alive_date',
                'comments'
            ]
        }),
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple
    )

    radio_fields = {
        'reason': admin.VERTICAL,
        'study_status': admin.VERTICAL,
        'info_source': admin.VERTICAL,
        'is_present': admin.VERTICAL,
        'survival_status': admin.VERTICAL,
    }
