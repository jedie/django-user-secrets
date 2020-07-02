from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from user_secrets_tests.views import DemoView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(DemoView.as_view())),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
