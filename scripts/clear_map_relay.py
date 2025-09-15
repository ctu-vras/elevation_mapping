#!/usr/bin/env python3
"""
clear_map_relay.py
Relays /elevation_map/clear_map_command  ─▶  /elevation_mapping/clear_map
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from nav2_msgs.srv import ClearEntireCostmap

class ClearMapRelay(Node):
    def __init__(self):
        super().__init__('clear_map_relay')

        # Client for the downstream service
        self._clear_map_client = self.create_client(Empty,
                                                    '/clear_map')

        # Block until the downstream service exists (optional but helpful)
        while not self._clear_map_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                '/elevation_mapping/clear_map not available … waiting')

        # Service that external nodes will call
        self._clear_cmd_srv = self.create_service(
            ClearEntireCostmap,
            '/elevation_map/clear_map_command',
            self._handle_clear_map_command)

        self.get_logger().info(
            'Relay ready: /elevation_map/clear_map_command  ➜  /clear_map')

    # --------------------------------------------------
    # Service callback
    # --------------------------------------------------
    def _handle_clear_map_command(self, request: ClearEntireCostmap.Request,
                                  response: ClearEntireCostmap.Response) -> ClearEntireCostmap.Response:
        self.get_logger().info('Received clear‑map command, relaying …')

        # Forward call asynchronously
        future = self._clear_map_client.call_async(Empty.Request())

        # Optionally wait a few seconds so we can log success/failure
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.done() and future.result() is not None:
            self.get_logger().info('Downstream /clear_map call succeeded')
        else:
            self.get_logger().error('Downstream /clear_map call failed or timed out')

        return response   # Empty response is fine


def main(args=None):
    rclpy.init(args=args)
    node = ClearMapRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
