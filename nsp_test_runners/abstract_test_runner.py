class AbstractTestRunner(object):

    def __init__(self):
        raise NotImplementedError()

    def run_test(self):
        result = self._run_test()
        if result:
            result = self._do_post_test_checks()

        return result

    def get_test_stats(self):
        raise NotImplementedError()

    def get_test_descriptive_result(self):
        raise NotImplementedError()

    def _initialize(self, target_name, test_parameters, target_history):
        self.target_name = target_name
        self.test_parameters = test_parameters
        self.test_history = target_history
        self.test_result = None
