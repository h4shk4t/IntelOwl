# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from greynoise import GreyNoise

from api_app.analyzers_manager import classes
from api_app.exceptions import AnalyzerRunException
from tests.mock_utils import MagicMock, if_mock_connections, patch


def mocked_greynoise(*args, **kwargs):
    QueryResponse = MagicMock()
    attrs = {"noise": True}
    QueryResponse.configure_mock(**attrs)
    Response = MagicMock(return_value=QueryResponse)
    return Response.return_value


class GreyNoiseAnalyzer(classes.ObservableAnalyzer):
    def set_params(self, params):
        self.api_version = params.get("greynoise_api_version", "v3")
        self.max_records_to_retrieve = int(params.get("max_records_to_retrieve", 500))

    def run(self):
        api_key = self._secrets["api_key_name"]
        if self.api_version == "v2":
            session = GreyNoise(
                api_key=api_key, integration_name="greynoise-intelowl-v1.0"
            )
            response = session.ip(self.observable_name)
            response |= session.riot(self.observable_name)
        elif self.api_version == "v3":
            # this allows to use this service without an API key set
            if not api_key:
                api_key = ""
            session = GreyNoise(
                api_key=api_key,
                integration_name="greynoise-community-intelowl-v1.0",
                offering="Community",
            )
            response = session.ip(self.observable_name)
        else:
            raise AnalyzerRunException(
                "Invalid API Version. " "Supported are: v2 (paid), v3 (community)"
            )

        return response

    @classmethod
    def _monkeypatch(cls):
        patches = [
            if_mock_connections(
                patch("greynoise.GreyNoise", side_effect=mocked_greynoise)
            )
        ]
        return super()._monkeypatch(patches=patches)
