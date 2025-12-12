import mmap
import os
import shutil
import time
from typing import Any, Dict, List, Tuple

import pytest
from assemblyline.common import forge
from assemblyline.common.importing import load_module_by_path
from assemblyline.common.uid import get_random_id
from assemblyline.odm.messages.task import Task as ServiceTask
from assemblyline_v4_service.common.request import ServiceRequest
from assemblyline_v4_service.common.task import Task

# The needle we search for in unpacked results to ensure the sample was sufficiently unpacked.
UNPACKED_TEST_NEEDLE = b"!UNPACK_KEY! a007be07-5ca3-421f-85b1-05befc9fe113 !UNPACK_KEY!"

# Force manifest location
os.environ["SERVICE_MANIFEST_PATH"] = os.path.join(os.path.dirname(__file__), "..", "service_manifest.yml")

# Setup folder locations
SAMPLES_FOLDER = os.path.join(os.path.dirname(__file__), "samples")

# Initialize test helper
service_class = load_module_by_path(
    "emuunpacker.emuunpacker.EmuUnpacker", os.path.join(os.path.dirname(__file__), "..")
)


def create_service_task(file_path) -> ServiceTask:
    fileinfo_keys = ["magic", "md5", "mime", "sha1", "sha256", "size", "type", "uri_info"]
    identify = forge.get_identify(use_cache=False)

    return ServiceTask(
        {
            "sid": get_random_id(),
            "metadata": {},
            "deep_scan": False,
            "depth": 2,
            "service_name": service_class.__name__,
            "service_config": {},
            "fileinfo": {
                k: v
                for k, v in identify.fileinfo(file_path, skip_fuzzy_hashes=True, calculate_entropy=False).items()
                if k in fileinfo_keys
            },
            "filename": os.path.basename(file_path),
            "min_classification": "TLP:C",
            "max_files": 501,
            "ttl": 3600,
            "temporary_submission_data": [],
            "tags": {},
        }
    )


def find_test_samples() -> List[str]:
    files = [os.path.join(SAMPLES_FOLDER, f) for f in os.listdir(SAMPLES_FOLDER)]

    return [f for f in files if os.path.isfile(f)]


def execute_service(sample) -> Tuple[Dict[str, Any], int]:
    start_time = time.time()
    cls = service_class({})
    cls.start()

    # Create the service request
    task = Task(create_service_task(sample))
    service_request = ServiceRequest(task)
    cls._working_directory = task.working_directory

    test_path = os.path.join("/tmp", task.fileinfo.sha256)
    shutil.copy2(sample, test_path)

    cls.execute(service_request)

    # Get results from the scan
    results = task.get_service_result()

    total_runtime = round(time.time() - start_time)

    return results, total_runtime


def assert_extraction_valid(extraction: Dict[str, Any]) -> None:
    with open(extraction["path"], "rb") as f:
        data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        assert data.find(UNPACKED_TEST_NEEDLE) >= 0


@pytest.mark.parametrize("sample", find_test_samples())
def test_sample(sample):
    results, total_runtime = execute_service(sample)

    extracted_sections = results["response"]["extracted"]

    assert len(extracted_sections) == 1

    assert_extraction_valid(extracted_sections[0])

    print(f"Time elapsed for {sample}: {total_runtime}s")
