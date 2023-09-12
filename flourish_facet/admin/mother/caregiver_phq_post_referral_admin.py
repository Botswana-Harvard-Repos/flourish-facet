from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ...admin_site import flourish_facet_admin
from ...forms import FacetCaregiverPhqPostReferralForm
from ...models import FacetCaregiverPhqPostReferral
from ..modeladmin_mixins import CrfModelAdminMixin


@admin.register(FacetCaregiverPhqPostReferral, site=flourish_facet_admin)
class FacetCaregiverPhqPostReferralAdmin(CrfModelAdminMixin, admin.ModelAdmin):

    form = FacetCaregiverPhqPostReferralForm

    fieldsets = (
        (None, {
            'fields': [
                'facet_visit',
                'report_datetime',
                'attended_referral',
                'support_ref_decline_reason',
                'support_ref_decline_reason_other',
                'emo_support',
                'no_support_reason',
                'no_support_reason_other',
                'emo_support_type',
                'emo_support_type_other',
                'emo_health_improved',
                'emo_health_improved_other',
                'percieve_counselor',
                'percieve_counselor_other',
                'satisfied_counselor',
                'additional_counseling'
            ]}
         ), audit_fieldset_tuple)

    radio_fields = {'attended_referral': admin.VERTICAL,
                    'support_ref_decline_reason': admin.VERTICAL,
                    'emo_support': admin.VERTICAL,
                    'no_support_reason': admin.VERTICAL,
                    'percieve_counselor': admin.VERTICAL,
                    'satisfied_counselor': admin.VERTICAL,
                    'additional_counseling': admin.VERTICAL, }

    filter_horizontal = ('emo_support_type', 'emo_health_improved')
