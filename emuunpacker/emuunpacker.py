"""This Assemblyline service unpacks binaries by leveraging the unicorn emulation library."""

from assemblyline.common import forge
from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.request import ServiceRequest
from assemblyline_v4_service.common.result import Result


class EmuUnpacker(ServiceBase):
    """This Assemblyline service unpacks binaries by leveraging the unicorn emulation library."""

    def execute(self, request: ServiceRequest):
        """Run the service."""

        result = Result()
        request.result = result
