from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..modeladmin_mixins import CrfModelAdminMixin
from ...admin_site import flourish_facet_admin
from ...forms import DepressionScreeningEdinBurghForm
from ...models import DepressionScreeningEdinBurgh


@admin.register(DepressionScreeningEdinBurgh, site=flourish_facet_admin)
class DepressionScreeningEdinBurghAdmin(CrfModelAdminMixin, admin.ModelAdmin):
    form = DepressionScreeningEdinBurghForm

    fieldsets = (
        (None, {
            'fields': [
                'facet_visit',
                'report_datetime',
                'able_to_laugh',
                'enjoyment_to_things',
                'self_blame',
                'anxious',
                'panicky',
                'coping',
                'sleeping_difficulty',
                'miserable_feeling',
                'unhappy',
                'self_harm',
                'depression_score'
            ]}
         ), audit_fieldset_tuple)

    radio_fields = {'able_to_laugh': admin.VERTICAL,
                    'enjoyment_to_things': admin.VERTICAL,
                    'self_blame': admin.VERTICAL,
                    'anxious': admin.VERTICAL,
                    'panicky': admin.VERTICAL,
                    'coping': admin.VERTICAL,
                    'sleeping_difficulty': admin.VERTICAL,
                    'miserable_feeling': admin.VERTICAL,
                    'unhappy': admin.VERTICAL,
                    'self_harm': admin.VERTICAL, }

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        return ('depression_score', ) + fields
