#!/usr/bin/python3

import logging
import sys
import json
from enum import Enum

from nsp_test_runners.dns_test_runner import DNSTestRunner
from nsp_test_runners.http_test_runner import HTTPTestRunner
from nsp_test_runners.nsp_alert_sender import NSPAlertSender

LOG_LINE_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_LEVEL = logging.DEBUG


class MethodsEnum(Enum):
    DNS = 'DNS'
    HTTP = 'HTTP'


METHOD_RUNNERS_DICT = {
    MethodsEnum.DNS.value: DNSTestRunner,
    MethodsEnum.HTTP.value: HTTPTestRunner
}


def _load_history_file(history_filename):
    try:
        with open(history_filename) as history_file:
            history = json.load(history_file)
            logging.debug('History file {} loaded'.format(history_filename))
    except OSError:
        logging.warning('History file {} not found. Initializing new history'.format(history_filename))
        history = {}

    return history


def _save_history_file(history, history_filename):
    with open(history_filename, 'w') as history_file:
        json.dump(history, history_file)


def run_tests(tests, history, nsp_alert_sender):
    for test_method in tests:
        method_name = test_method['method']
        method_targets = test_method['targets']
        method_runner = METHOD_RUNNERS_DICT[method_name]

        for test_target in method_targets:
            target_name = test_target['target_name']
            test_parameters = test_target['parameters']

            # check if target history exists, otherwise start a new empty dict
            try:
                target_history = history[method_name][target_name]
            except KeyError:
                target_history = dict()

            logging.info('Handling {} test on target {} with parameters {}'.format(
                method_name, target_name, test_parameters))

            if method_name in ['DNS', 'HTTP']:
                test_runner = method_runner(target_name, test_parameters, target_history)
                result = test_runner.run_test()
                logging.debug('Test result = {}'.format(result))

                if result:
                    logging.info(test_runner.get_test_descriptive_result())

                    # update history
                    test_stats = test_runner.get_test_stats()
                    if len(test_stats) > 0:
                        method_dict = history.setdefault(method_name, dict())
                        target_stats = method_dict.setdefault(target_name, list())
                        target_stats.append(test_stats)

                else:
                    logging.error(test_runner.get_test_descriptive_result())
                    nsp_alert_sender.send_alert(test_runner.get_test_descriptive_result())
                    logging.debug('Sent the email alerts successfully')


def main(args):

    logging.basicConfig(level=LOG_LEVEL,
                        format=LOG_LINE_FORMAT)

    if len(args) != 1:
        logging.error('usage: nsp.py <config_file.json>')
        exit(1)

    config_filename = args[0]

    with open(config_filename) as config_file:
        config = json.load(config_file)
        logging.debug('Configuration file {} loaded'.format(config_filename))

    nsp_alerts_email = config['general']['nsp_email_address']
    nsp_email_pwd = config['general']['nsp_email_pwd']
    alert_email_targets = config['general']['alert_email_targets']
    history_filename = config['general']['history_file']
    tests = config['tests']

    # load history file or initialize new dict if it does not exist
    history = _load_history_file(history_filename)

    nsp_alert_sender = NSPAlertSender(nsp_alerts_email, nsp_email_pwd, alert_email_targets)

    run_tests(tests, history, nsp_alert_sender)

    _save_history_file(history, history_filename)


if __name__ == '__main__':
    main(sys.argv[1:])