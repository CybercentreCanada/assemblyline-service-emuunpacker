import os
import threading
from os import PathLike
from typing import Optional

from unipacker.core import Sample, SimpleClient, UnpackerEngine
from unipacker.utils import RepeatedTimer

from .error import UnpackError


def unpack(sample_path: str | PathLike, result_directory: str | PathLike, *, timeout_seconds: Optional[float]) -> str:
    dest_file = os.path.join(result_directory, f"unpacked_{os.path.basename(sample_path)}")

    try:
        sample = Sample(sample_path, auto_default_unpacker=True)
        engine = UnpackerEngine(sample, dest_file)
    except Exception as e:
        raise UnpackError("Error parsing the sample as an executable binary file.") from e

    event = threading.Event()
    client = SimpleClient(event)

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
        raise UnpackError("The unpack process failed to produce any output.")

    return dest_file
