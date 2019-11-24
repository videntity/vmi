import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404,  HttpResponse
from django.utils.translation import ugettext_lazy as _
# from .emails import send_new_org_account_approval_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from ..accounts.models import Organization
from .decorators import group_required
from datetime import datetime
import csv
from collections import OrderedDict
# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)

# @group_required("some-group")
def orgs_and_agents_report(request):
    filename = datetime.now().strftime('%m-%d-%Y_%H:%M:%S') + '.csv'
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    rows = []
    row = ["animals", "plants"]
    rows.append(row)
    row = ["cat", "apple tree"]
    rows.append(row)
    row = ["dog", "grass"]
    rows.append(row)


    writer = csv.writer(response, delimiter=',')
    for r in rows:
        # filtered_string = "".join(s for s in c if s in string.printable)
        writer.writerows([r])
    return response


    

