import unittest
import json

from app.modules.cloud_fog.controller import Cloud_fogController


def test_index():
    cloud_fog_controller = Cloud_fogController()
    result = cloud_fog_controller.index()
    assert result == {'message': 'Hello, World!'}
