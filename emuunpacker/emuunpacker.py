"""An Assemblyline service to unpack binaries by leveraging the unicorn emulation library."""

import os
import tempfile

from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.request import ServiceRequest
from assemblyline_v4_service.common.result import Result, ResultSection

from .unpacker import UnpackError, unpack


class EmuUnpacker(ServiceBase):
    """Assemblyline service unpacks binaries by leveraging the unicorn emulation library."""

    def execute(self, request: ServiceRequest) -> None:
        """Run the service. Returns the result or None if no result was produced."""
        result = Result()
        request.result = result

        results_dir = tempfile.mkdtemp(dir=self.working_directory)

        try:
            unpacked_result = unpack(request.file_path, results_dir, timeout_seconds=60 * 5)
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
