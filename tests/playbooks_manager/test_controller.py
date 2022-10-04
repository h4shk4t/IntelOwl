import os

from django.test import TransactionTestCase

from api_app.models import Job
from api_app.serializers import PlaybookObservableAnalysisSerializer
from intel_owl.tasks import start_playbooks
from tests import PollingFunction


class PlaybooksScriptTestCase(TransactionTestCase):
    # attrs
    test_job: Job

    def setUp(self):
        playbooks_to_test = os.environ.get("TEST_PLAYBOOKS", "").split(",")
        self.playbooks_to_test = (
            playbooks_to_test
            if len(playbooks_to_test) and len(playbooks_to_test[0])
            else []
        )
        return super().setUp()

    def tearDown(self):
        self.test_job.delete()
        return super().tearDown()

    def test_start_playbooks_observable(self, *args, **kwargs):
        print(f"\n[START] -----{self.__class__.__name__}.test_start_playbooks----")

        TEST_IP = os.environ.get("TEST_IP", "1.1.1.1")

        data = {
            "observables": ["ip", TEST_IP],
            "playbooks_requested": self.playbooks_to_test,
        }

        serializer = PlaybookObservableAnalysisSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        self.test_job = serializer.save()

        print(
            f"[REPORT] Job:{self.test_job.pk}, status:'{self.test_job.status}',",
            f"Playbooks: {self.test_job.playbooks_to_execute}",
        )

        start_playbooks(self.test_job.id, {})

        return PollingFunction(self, "start_playbooks")
