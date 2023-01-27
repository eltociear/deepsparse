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

import os

import numpy

import pytest
from deepsparse import Pipeline
from tests.utils import mock_engine


@pytest.mark.parametrize(
    "group_name, pipeline_name, inputs, expected_logs",
    [
        (
            "image_classification",
            "image_classification",
            {"images": [numpy.ones((3, 224, 224))] * 2},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/image_classification_logs.txt",
        ),
        (
            "image_classification",
            "image_classification",
            {"images": numpy.ones((2, 3, 224, 224))},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/image_classification_logs.txt",
        ),
        (
            "object_detection",
            "yolo",
            {"images": [numpy.ones((3, 640, 640))] * 2},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/object_detection_logs.txt",
        ),
        (
            "object_detection",
            "yolo",
            {"images": numpy.ones((2, 3, 640, 640))},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/object_detection_logs.txt",
        ),
        (
            "segmentation",
            "yolact",
            {"images": [numpy.ones((3, 640, 640))] * 2},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/segmentation_logs.txt",
        ),
        (
            "segmentation",
            "yolact",
            {"images": numpy.ones((2, 3, 640, 640))},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/segmentation_logs.txt",
        ),
        (
            "sentiment_analysis",
            "sentiment_analysis",
            {"sequences": "the food tastes great"},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/sentiment_analysis_logs_1.txt",
        ),
        (
            "sentiment_analysis",
            "sentiment_analysis",
            {"sequences": ["the food tastes great", "the food tastes bad"]},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/sentiment_analysis_logs_2.txt",
        ),
        (
            "sentiment_analysis",
            "sentiment_analysis",
            {
                "sequences": [
                    ["the food tastes great", "the food tastes bad"],
                    ["the food tastes great", "the food tastes bad"],
                ]
            },
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/sentiment_analysis_logs_3.txt",
        ),
        (
            "zero_shot_text_classification",
            "zero_shot_text_classification",
            {"sequences": "the food tastes great", "labels": ["politics", "food"]},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/zero_shot_text_classification_logs_1.txt",
        ),
        (
            "zero_shot_text_classification",
            "zero_shot_text_classification",
            {
                "sequences": ["the food tastes great", "the food tastes bad"],
                "labels": ["politics", "food"],
            },
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/zero_shot_text_classification_logs_2.txt",
        ),
        (
            "token_classification",
            "token_classification",
            {"inputs": "the food tastes great"},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/token_classification_logs_1.txt",
        ),
        (
            "token_classification",
            "token_classification",
            {"inputs": ["the food tastes great", "the food tastes bad"]},
            "tests/deepsparse/loggers/metric_functions/template_functions/template_logs/token_classification_logs_2.txt",
        ),
    ],
)
@mock_engine(rng_seed=0)
def test_group_name(mock_engine, group_name, pipeline_name, inputs, expected_logs):
    yaml_config = """
    loggers:
        list_logger:
            path: tests/deepsparse/loggers/helpers.py:ListLogger
    add_predefined:
    - func: {group_name}"""

    pipeline = Pipeline.create(
        pipeline_name, logger=yaml_config.format(group_name=group_name)
    )
    pipeline(**inputs)
    logs = pipeline.logger.loggers[0].logger.loggers[0].calls
    data_logging_logs = [log for log in logs if "DATA" in log]
    if os.environ["GENERATE_LOGS"] == "1":
        dir = os.path.dirname(expected_logs)
        os.makedirs(dir, exist_ok=True)
        with open(expected_logs, "w") as f:
            f.write("\n".join(data_logging_logs))

    with open(expected_logs, "r") as f:
        expected_logs = f.read().splitlines()
    for log, expected_log in zip(data_logging_logs, expected_logs):
        assert log == expected_log


yaml_config = """
loggers:
    list_logger:
        path: tests/deepsparse/loggers/helpers.py:ListLogger
add_predefined:
    - func: image_classification
      frequency: 2
data_logging:
    pipeline_inputs.images:
    - func: image_shape
      frequency: 2"""


@pytest.mark.parametrize(
    "yaml_config",
    [
        yaml_config,
    ],
)
@mock_engine(rng_seed=0)
def test_no_function_duplicates_within_template(mock_engine, yaml_config):
    with pytest.raises(ValueError):
        Pipeline.create("image_classification", logger=yaml_config)
