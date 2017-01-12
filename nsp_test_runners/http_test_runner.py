import http.client
from enum import Enum
from urllib.parse import urlparse
import socket

from nsp_test_runners.abstract_test_runner import AbstractTestRunner

HTTP_STATUS_ERROR_OFFSET = 400

class HTTPFailureReason(Enum):
    RESOLUTION_FAILED = 'dns resoultion failed'
    BAD_HTTP_STATUS = 'bad_http_status'
    UNEXPECTED_ERROR = 'unexpected error'


class HTTPTestRunner(AbstractTestRunner):

    def _initialize(self):
        self._ip_address = None
        self._http_status = None
        self._failure_reason = None

    def _run_test(self):

        test_result = False
        parse_result = urlparse(self.target_name)
        try:
            conn = http.client.HTTPConnection(parse_result.netloc)
            conn.request("GET", parse_result.path)
            response = conn.getresponse()
            self._http_status = response.status
            if self._http_status > HTTP_STATUS_ERROR_OFFSET:
                self._failure_reason = HTTPFailureReason.BAD_HTTP_STATUS
            else:
                test_result = True
        except socket.gaierror:
            self._failure_reason = HTTPFailureReason.RESOLUTION_FAILED
        except:
            self._failure_reason = HTTPFailureReason.OTHER_REASON

        self.test_result = test_result

    def _do_post_test_checks(self):
        return True

    def get_test_stats(self):
        return dict()

    def get_test_descriptive_result(self):
        if self.test_result:
            return 'Successfully connected to {} - (Response status: {:d})'.format(self.target_name, self._http_status)
        else:
            return 'Failed to connect to {} - Failure reason: {} (Response status: {})'.format(
                self.target_name, self._failure_reason.value, self._http_status)