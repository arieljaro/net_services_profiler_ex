import http.client
from enum import Enum
from urllib.parse import urlparse
import socket

import time

from nsp_test_runners.abstract_test_runner import AbstractTestRunner

HTTP_STATUS_ERROR_OFFSET = 400


class HTTPFailureReason(Enum):
    RESOLUTION_FAILED = 'dns resoultion failed'
    BAD_HTTP_STATUS = 'bad_http_status'
    LATENCY_OVER_THRESHOLD = 'latency over threshold'
    BANDWIDTH_OVER_THRESHOLD = 'bandwidth over threshold'
    UNEXPECTED_ERROR = 'unexpected error'


class HTTPTestRunner(AbstractTestRunner):

    def _initialize(self):
        self._response = None
        self._failure_reason = None
        self._connection_type = None
        self._latency = None

    def _run_test(self):

        test_result = False
        parse_result = urlparse(self.target_name)

        try:
            self._connection_type = 'HTTPSConnection' if parse_result.scheme == 'https' else 'HTTPConnection'
            http_connection_type = http.client.HTTPSConnection if parse_result.scheme == 'https' \
                else http.client.HTTPConnection
            conn = http_connection_type(parse_result.netloc)

            self._latency = -time.time()
            conn.request("GET", parse_result.path)
            self._latency += time.time()

            self._response = conn.getresponse()

            # calculate bandwidth
            if self._http_status > HTTP_STATUS_ERROR_OFFSET:
                self._failure_reason = HTTPFailureReason.BAD_HTTP_STATUS
            else:
                test_result = True
                contents = self._response.read()
                self._bandwidth = (len(contents) / self._latency) / 1000.0

        except socket.gaierror:
            self._failure_reason = HTTPFailureReason.RESOLUTION_FAILED
        except:
            self._failure_reason = HTTPFailureReason.UNEXPECTED_ERROR

        self.test_result = test_result

    def _do_post_test_checks(self):
        latency_threshold = self.test_parameters.get('latency_threshold')
        last_latency = self.test_history[-1]['latency']
        if (latency_threshold is not None) and (self._latency > last_latency * latency_threshold):
            self._failure_reason = HTTPFailureReason.LATENCY_OVER_THRESHOLD
            self.test_result = False

        bandwidth_threshold = self.test_parameters.get('bandwidth_threshold')
        last_bandwidth = self.test_history[-1]['bandwidth']
        if (bandwidth_threshold is not None) and (self._bandwidth > last_bandwidth * bandwidth_threshold):
            self._failure_reason = HTTPFailureReason.BANDWIDTH_OVER_THRESHOLD
            self.test_result = False

    def get_test_stats(self):
        if self.test_result or self._has_failed_on_post_checks():
            return {
                'bandwidth': self._bandwidth,
                'latency': self._latency
            }

        else:
            return dict()

    def _has_failed_on_post_checks(self):
        return self._failure_reason in [HTTPFailureReason.LATENCY_OVER_THRESHOLD,
                                        HTTPFailureReason.BANDWIDTH_OVER_THRESHOLD]

    def get_test_descriptive_result(self):
        if self.test_result:
            return 'Successful {} to {} - (Response status: {:d}) ' \
                   '[Download bandwidth of {:.2f} KBps, latency of {:.2f} seconds]'.format(
                self._connection_type, self.target_name, self._http_status, self._bandwidth, self._latency)
        else:
            failure_str = 'Failed {} to connect to {} - Failure reason: {} (Response status: {})'.format(
                self._connection_type, self.target_name, self._failure_reason.value, self._http_status)
            if self._has_failed_on_post_checks():
                failure_str += ' [Download bandwidth of {:.2f} KBps, latency of {:.2f} seconds]'.format(
                    self._bandwidth, self._latency)
            return failure_str

    @property
    def _http_status(self):
        if self._response is None:
            return None
        else:
            return self._response.status
