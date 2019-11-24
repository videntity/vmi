# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import orgs_and_agents_report


# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^org-and-agent-report$',
        orgs_and_agents_report, name='orgs_and_agents_report'),

]
