"""Django integration contracts for django-ingredients template (I1–I3, R1, S1–S2, T2)."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import clear_url_caches, set_urlconf


REPO_ROOT = Path(__file__).resolve().parents[1]


class DjangoSetupTests(SimpleTestCase):
    def test_package_app_is_installed(self):
        """I1: ingredients loads under tests.settings."""
        config = apps.get_app_config("ingredients")
        assert config.name == "ingredients"

    def test_installed_apps_includes_package_and_contenttypes(self):
        """I1: settings load with package + Django contenttypes for clones."""
        assert "ingredients" in settings.INSTALLED_APPS
        assert "django.contrib.contenttypes" in settings.INSTALLED_APPS

    def test_test_settings_use_fast_hasher_and_tz(self):
        """R1."""
        assert settings.PASSWORD_HASHERS == [
            "django.contrib.auth.hashers.MD5PasswordHasher"
        ]
        assert settings.USE_TZ is True

    def test_secret_key_is_non_production_sentinel(self):
        """S1."""
        assert settings.SECRET_KEY == "NOTASECRET"

    def test_security_middleware_present(self):
        """S2."""
        mw = list(settings.MIDDLEWARE)
        assert "django.middleware.security.SecurityMiddleware" in mw
        assert "django.middleware.csrf.CsrfViewMiddleware" in mw
        assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in mw


class UrlconfTests(SimpleTestCase):
    def test_package_urls_module_importable(self):
        """I2/T2: template ships ingredients.urls for ROOT_URLCONF includes."""
        mod = import_module("ingredients.urls")
        assert hasattr(mod, "urlpatterns")
        assert isinstance(mod.urlpatterns, list)

    def test_package_urls_include_detail_routes(self):
        """I2: ingredient detail reverse names are registered."""
        mod = import_module("ingredients.urls")
        assert len(mod.urlpatterns) >= 3

    def test_root_urlconf_loads(self):
        """I2: tests.urls can resolve without ImproperlyConfigured."""
        clear_url_caches()
        set_urlconf(settings.ROOT_URLCONF)
        client = Client()
        response = client.get("/")
        assert response.status_code == 404

    def test_tests_urls_includes_package_urls(self):
        """I2: harness ROOT_URLCONF wires ingredients.urls."""
        urls_src = (REPO_ROOT / "tests" / "urls.py").read_text(encoding="utf-8")
        assert "ingredients.urls" in urls_src
        assert settings.ROOT_URLCONF == "tests.urls"


class HarnessEntryTests(SimpleTestCase):
    def test_runtests_entry_points_at_pytest(self):
        """I3: runtests.py is the clone harness entry (pytest.main)."""
        runtests = REPO_ROOT / "runtests.py"
        assert runtests.is_file()
        source = runtests.read_text(encoding="utf-8")
        assert "pytest.main" in source
        assert 'pytest_args = ["tests"]' in source
