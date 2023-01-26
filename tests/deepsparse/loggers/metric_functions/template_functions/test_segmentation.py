# Copyright (c) 2021 - present / Neuralmagic, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import numpy
from tests.utils import mock_engine
from deepsparse import Pipeline

yaml_config = """
loggers:
    list_logger:
        path: tests/deepsparse/loggers/helpers.py:ListLogger
data_logging:
    predefined:
    - func: segmentation
      frequency: 1"""

expected_logs = """identifier:yolact/pipeline_inputs.images__image_shape, value:{'channels': 3, 'dim_0': 640, 'dim_1': 640}, category:MetricCategories.DATA
identifier:yolact/pipeline_inputs.images__mean_pixels_per_channel, value:{'channel_0': 1.0, 'channel_1': 1.0, 'channel_2': 1.0}, category:MetricCategories.DATA
identifier:yolact/pipeline_inputs.images__std_pixels_per_channel, value:{'channel_0': 0.0, 'channel_1': 0.0, 'channel_2': 0.0}, category:MetricCategories.DATA
identifier:yolact/pipeline_inputs.images__fraction_zeros, value:0.0, category:MetricCategories.DATA
identifier:yolact/pipeline_outputs.classes__detected_classes, value:{'7': 6, '10': 4, '23': 6, '38': 2, '41': 2, '69': 2, '67': 2, '8': 2, '54': 2, '16': 2, '78': 2, '39': 4, '73': 2, '32': 4, '58': 2, '31': 2, '40': 6, '22': 2, '46': 2, '36': 2, '47': 2, '30': 4, '1': 2, '57': 2, '60': 2, '25': 2, '64': 4, '26': 2, '29': 2, '5': 2, '52': 2, '37': 2, '70': 2, '3': 2, '65': 2, '56': 2, '9': 2, '63': 2, '79': 2}, category:MetricCategories.DATA
identifier:yolact/pipeline_outputs.classes__number_detected_objects, value:[50, 50], category:MetricCategories.DATA
identifier:yolact/pipeline_outputs.scores__mean_score_per_detection, value:[0.9999835777282715, 0.9999835777282715], category:MetricCategories.DATA
identifier:yolact/pipeline_outputs.scores__std_score_per_detection, value:[8.525441680612083e-06, 8.525441680612083e-06], category:MetricCategories.DATA
"""  # noqa E501


@pytest.mark.parametrize(
    "config, inp, num_iterations, expected_logs",
    [
        (yaml_config, [numpy.ones((3, 640, 640))] * 2, 1, expected_logs),
        (yaml_config, numpy.ones((2, 3, 640, 640)), 1, expected_logs),
    ],
)
@mock_engine(rng_seed=0)
def test_end_to_end(mock_engine, config, inp, num_iterations, expected_logs):
    pipeline = Pipeline.create("yolact", logger=config)
    for _ in range(num_iterations):
        pipeline(images=inp)

    logs = pipeline.logger.loggers[0].logger.loggers[0].calls
    data_logging_logs = [log for log in logs if "DATA" in log]
    for log, expected_log in zip(data_logging_logs, expected_logs.splitlines()):
        assert log == expected_log