"""An Assemblyline service to unpack binaries by leveraging the unicorn emulation library."""

import os
import tempfile

from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.request import ServiceRequest
from assemblyline_v4_service.common.result import Result, ResultSection

from .unpacker import UnpackError, unpack


class EmuUnpacker(ServiceBase):
    """Assemblyline service unpacks binaries by leveraging the unicorn emulation library."""

    # Aim to complete processing within a safe margin of seconds before configured timeout.
    TIMEOUT_SAFETY_MARGIN = 5

    # Time allocated after emulation to produce a dump
    TIME_ALLOCATION_DUMP = 5

    # To be useful, at least 2 seconds should be allocated for emulation runtime
    TIME_ALLOCATION_EMULATION = 2

    def execute(self, request: ServiceRequest) -> None:
        """Run the service. Returns the result or None if no result was produced."""
        result = Result()
        request.result = result

        emulation_runtime = self.service_attributes.timeout - EmuUnpacker.SERVICE_TIMEOUT_SAFETY_MARGIN
        emulation_runtime -= EmuUnpacker.TIME_ALLOCATION_DUMP

        if emulation_runtime < EmuUnpacker.TIME_ALLOCATION_EMULATION:
            self.log.error("Could not allocate sufficient time for emulation runtime. Increase service timeout config.")
            return

        results_dir = tempfile.mkdtemp(dir=self.working_directory)

        try:
            unpacked_result = unpack(request.file_path, results_dir, timeout_seconds=emulation_runtime)
        except UnpackError as e:
            self.log.error(f"EmuUnpacker extractor failed:\n{e}")
            return

        display_name = os.path.basename(unpacked_result)
        result_section = ResultSection(f"{display_name} successfully unpacked!")

        if not request.add_extracted(
            unpacked_result,
            display_name,
            f"Unpacked from {request.sha256}",
            safelist_interface=self.api_interface,
        ):
            result_section.body = "This extracted file will not been re-submitted due to being known as safe."

        request.result.add_section(result_section)
