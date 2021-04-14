"""vmi URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from oauth2_provider import views as oauth2_views
from .oauth2_views import ApplicationRegistration, ApplicationUpdate
from apps.oidc import views as oidc_views
from apps.home.views import home, user_search, user_profile
from django.conf import settings
from django.conf.urls.static import static

# Copyright Videntity Systems, Inc.

admin.site.site_header = "Verify My Identity (VMI) Admin"
admin.site.site_title = "Verify My Identity (VMI) Admin Portal"
admin.site.index_title = "Verify My Identity Administration"

oauth2_base_urlpatterns = [
    url(r"^authorize/$",
        oidc_views.AuthorizationView.as_view(),
        name="authorize"),
    url(r"^token/$",
        oauth2_views.TokenView.as_view(),
        name="token"),
    url(r"^revoke_token/$",
        oauth2_views.RevokeTokenView.as_view(),
        name="revoke-token"),
    url(r"^introspect/$",
        oauth2_views.IntrospectTokenView.as_view(),
        name="introspect"),
]


oauth2_management_urlpatterns = [
    # Application management views
    url(r"^applications/$",
        oauth2_views.ApplicationList.as_view(),
        name="list"),
    url(r"^applications/register/$",
        ApplicationRegistration.as_view(),
        name="register"),
    url(r"^applications/(?P<pk>[\w-]+)/$",
        oauth2_views.ApplicationDetail.as_view(),
        name="detail"),
    url(r"^applications/(?P<pk>[\w-]+)/delete/$",
        oauth2_views.ApplicationDelete.as_view(),
        name="delete"),
    url(r"^applications/(?P<pk>[\w-]+)/update/$",
        ApplicationUpdate.as_view(),
        name="update"),
    # Token management views
    url(r"^authorized_tokens/$",
        oauth2_views.AuthorizedTokensListView.as_view(),
        name="authorized-token-list"),
    url(r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$",
        oauth2_views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete"),
]


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('o/',
         include((oauth2_management_urlpatterns + oauth2_base_urlpatterns,
                  'oauth2_provider'))),
    path('auth/',
         include('django.contrib.auth.urls')),
    path('accounts/',
         include('apps.accounts.urls')),
    path('ial/',
         include('apps.ial.urls')),
    path('reports/',
         include('apps.reports.urls')),
    path('dcrp/',
         include('apps.dynamicreg.urls')),
    path('testclient/',
         include('apps.testclient.urls')),
    path('.well-known/',
         include('apps.oidc.wellknown_urls')),
    path('o/', include(('apps.oidc.urls', 'oidc'), namespace='oidc')),
    path('search', user_search, name='user_search'),
    url("^search/organization/members/(?P<org_slug>[^/]+)/$", user_search,
        name='member_search_org_slug'),
    path('device/',
         include(('apps.fido.urls', 'fido'), namespace='fido')),
    url("^profile/(?P<subject>[^/]+)$",
        user_profile, name='user_profile_subject'),
    url(r"^profile/", user_profile, name='user_profile'),
    path('api/', include('apps.api.urls')),
    url('social-auth/', include('social_django.urls', namespace='social')),
    path('chop/', include('apps.chop.urls')),
    path('home/', include('apps.home.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
