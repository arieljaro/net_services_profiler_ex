import socket
from enum import Enum

from nsp_test_runners.abstract_test_runner import AbstractTestRunner


class DNSFailureReason(Enum):
    RESOLUTION_FAILED = 'dns resoultion failed'
    OTHER_REASON = 'other reason'


class DNSTestRunner(AbstractTestRunner):

    def _initialize(self):
        self._ip_address = None
        self._failure_reason = None

    def _run_test(self):

        test_result = False
        try:
            self._ip_address = socket.gethostbyname(self.target_name)
            test_result = True
        except socket.gaierror:
            self._failure_reason = DNSFailureReason.RESOLUTION_FAILED
        except Exception as e:
            self._failure_reason = DNSFailureReason.OTHER_REASON

        self.test_result = test_result

    def _do_post_test_checks(self):
        return True

    def get_test_stats(self):
        return dict()

    def get_test_descriptive_result(self):
        if self.test_result:
            return 'Successfully performed dns lookup of {} - {}'.format(self.target_name, self._ip_address)
        else:
            return 'Failed to perform dns lookup of {} - Failure reason: {}'.format(
                self.target_name, self._failure_reason.value)
