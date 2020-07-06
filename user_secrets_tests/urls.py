from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from user_secrets_tests.views.display import DisplayExampleSecretView
from user_secrets_tests.views.edit import EditExampleSecretView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('demo/', login_required(DisplayExampleSecretView.as_view())),
    path('', login_required(EditExampleSecretView.as_view())),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
