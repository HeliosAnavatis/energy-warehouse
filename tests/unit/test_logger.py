# tests/unit/test_logger.py

import logging

from utils.logger import get_logger


def test_returns_logger_instance():

    logger = get_logger("test")

    assert isinstance(
        logger,
        logging.Logger,
    )


def test_logger_name():

    logger = get_logger("my_logger")

    assert logger.name == "my_logger"


def test_logger_level():

    logger = get_logger(
        "level_test",
        logging.DEBUG,
    )

    assert logger.level == logging.DEBUG


def test_logger_has_single_handler():

    logger = get_logger(
        "handler_test"
    )

    assert len(
        logger.handlers
    ) == 1


def test_duplicate_calls_do_not_add_handlers():

    logger1 = get_logger(
        "duplicate_test"
    )

    logger2 = get_logger(
        "duplicate_test"
    )

    assert logger1 is logger2

    assert len(
        logger1.handlers
    ) == 1


def test_propagation_disabled():

    logger = get_logger(
        "propagation_test"
    )

    assert logger.propagate is False