from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel, FormAsJSONModelMixin
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_visit_schedule.model_mixins import SubjectScheduleCrfModelMixin
from edc_visit_tracking.model_mixins import CrfModelMixin as BaseCrfModelMixin
from edc_visit_tracking.model_mixins import PreviousVisitModelMixin

from ..facet_child_visit import FacetChildVisit


class CrfModelMixin(BaseCrfModelMixin, SubjectScheduleCrfModelMixin,
                    RequiresConsentFieldsModelMixin, PreviousVisitModelMixin,
                    UpdatesCrfMetadataModelMixin, SiteModelMixin,
                    FormAsJSONModelMixin, ReferenceModelMixin, BaseUuidModel):

    """ Base model for all scheduled models
    """
    offschedule_compare_dates_as_datetimes = True
    facet_child_visit = models.OneToOneField(
        FacetChildVisit, on_delete=PROTECT)
    crf_date_validator_cls = None

    @property
    def subject_identifier(self):
        return self.facet_child_visit.appointment.subject_identifier

    def natural_key(self):
        return self.facet_child_visit.natural_key()

    natural_key.dependencies = [
        'flourish_facet.facetchildvisit',
        'sites.Site',
        'flourish_facet.Appointment']

    class Meta:
        abstract = True
