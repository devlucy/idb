#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

import asyncio
import logging
import warnings
from typing import Dict, Optional

import idb.grpc.ipc_loader as ipc_loader
from grpclib.client import Channel
from idb.common.companion import CompanionClient
from idb.grpc.idb_grpc import CompanionServiceStub
from idb.common.types import IdbClientBase


# this is to silence the channel not closed warning
# https://github.com/vmagamedov/grpclib/issues/58
warnings.filterwarnings(action="ignore", category=ResourceWarning)


class IdbGRPCClient(IdbClientBase):
    def __init__(
        self,
        port: int,
        host: str,
        target_udid: Optional[str],
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.port: int = port
        self.host: str = host
        self.logger: logging.Logger = (
            logger if logger else logging.getLogger("idb_grpc_client")
        )
        self.target_udid = target_udid
        # TODO: T39585325
        self.channel = Channel(host, port, loop=asyncio.get_event_loop())
        self.stub = CompanionServiceStub(channel=self.channel)
        for (call_name, f) in ipc_loader.client_calls(
            daemon_provider=self.provide_client
        ):
            setattr(self, call_name, f)

    def provide_client(self) -> CompanionClient:
        return CompanionClient(
            stub=self.stub, is_local=True, udid=self.target_udid, logger=self.logger
        )

    @property
    def metadata(self) -> Dict[str, str]:
        if self.target_udid:
            return {"udid": self.target_udid}
        else:
            return {}