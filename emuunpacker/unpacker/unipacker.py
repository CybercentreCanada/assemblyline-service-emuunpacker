import math
import os
import sys
import threading
from os import PathLike
from typing import Optional

from unipacker.core import Sample, SimpleClient, UnpackerEngine
from unipacker.utils import RepeatedTimer

from .error import UnpackException


def unpack(sample_path: str | PathLike, result_directory: str | PathLike, *, timeout_seconds: Optional[float]) -> str:
    try:
        sample = Sample(sample_path, auto_default_unpacker=True)
    except Exception as e:
        raise UnpackException("Error parsing the sample as an executable binary file.") from e

    dest_file = os.path.join(result_directory, f"unpacked_{os.path.basename(sample.path)}")

    event = threading.Event()
    client = SimpleClient(event)

    engine = UnpackerEngine(sample, dest_file)
    engine.register_client(client)

    if timeout_seconds is not None:
        timeout = RepeatedTimer(timeout_seconds, engine.stop)
        timeout.start()

    threading.Thread(target=engine.emu).start()

    event.wait()

    if timeout_seconds is not None:
        timeout.stop()

    engine.stop()

    if not os.path.exists(dest_file):
        raise UnpackException("The unpack process failed to produce any output.")

    return dest_file
