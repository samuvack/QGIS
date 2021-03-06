# -*- coding: utf-8 -*-
"""QGIS Unit tests for QgsMapRendererCache.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = 'Nyall Dawson'
__date__ = '1/02/2017'
__copyright__ = 'Copyright 2017, The QGIS Project'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import qgis  # NOQA

from qgis.core import (QgsMapRendererCache,
                       QgsRectangle,
                       QgsVectorLayer,
                       QgsProject)
from qgis.testing import start_app, unittest
from qgis.PyQt.QtGui import QImage
start_app()


class TestQgsMapRendererCache(unittest.TestCase):

    def testSetCacheImages(self):
        cache = QgsMapRendererCache()
        # not set image
        im = cache.cacheImage('littlehands')
        self.assertTrue(im.isNull())
        self.assertFalse(cache.hasCacheImage('littlehands'))

        # set image
        im = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('littlehands', im)
        self.assertFalse(im.isNull())
        self.assertEqual(cache.cacheImage('littlehands'), im)
        self.assertTrue(cache.hasCacheImage('littlehands'))

        # test another not set image when cache has images
        self.assertTrue(cache.cacheImage('bad').isNull())
        self.assertFalse(cache.hasCacheImage('bad'))

        # clear cache image
        cache.clearCacheImage('not in cache') # no crash!
        cache.clearCacheImage('littlehands')
        im = cache.cacheImage('littlehands')
        self.assertTrue(im.isNull())
        self.assertFalse(cache.hasCacheImage('littlehands'))

        # clear whole cache
        im = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('littlehands', im)
        self.assertFalse(im.isNull())
        self.assertTrue(cache.hasCacheImage('littlehands'))
        cache.clear()
        im = cache.cacheImage('littlehands')
        self.assertTrue(im.isNull())
        self.assertFalse(cache.hasCacheImage('littlehands'))

    def testInit(self):
        cache = QgsMapRendererCache()
        extent = QgsRectangle(1, 2, 3, 4)
        self.assertFalse(cache.init(extent, 1000))

        # add a cache image
        im = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('layer', im)
        self.assertFalse(cache.cacheImage('layer').isNull())
        self.assertTrue(cache.hasCacheImage('layer'))

        # re init, without changing extent or scale
        self.assertTrue(cache.init(extent, 1000))

        # image should still be in cache
        self.assertFalse(cache.cacheImage('layer').isNull())
        self.assertTrue(cache.hasCacheImage('layer'))

        # reinit with different scale
        self.assertFalse(cache.init(extent, 2000))
        # cache should be cleared
        self.assertTrue(cache.cacheImage('layer').isNull())
        self.assertFalse(cache.hasCacheImage('layer'))

        # readd image to cache
        cache.setCacheImage('layer', im)
        self.assertFalse(cache.cacheImage('layer').isNull())
        self.assertTrue(cache.hasCacheImage('layer'))

        # change extent
        self.assertFalse(cache.init(QgsRectangle(11, 12, 13, 14), 2000))
        # cache should be cleared
        self.assertTrue(cache.cacheImage('layer').isNull())
        self.assertFalse(cache.hasCacheImage('layer'))

    def testRequestRepaintSimple(self):
        """ test requesting repaint with a single dependent layer """
        layer = QgsVectorLayer("Point?field=fldtxt:string",
                               "layer", "memory")
        QgsProject.instance().addMapLayers([layer])
        self.assertTrue(layer.isValid())

        # add image to cache
        cache = QgsMapRendererCache()
        im = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('xxx', im, [layer])
        self.assertFalse(cache.cacheImage('xxx').isNull())
        self.assertTrue(cache.hasCacheImage('xxx'))

        # trigger repaint on layer
        layer.triggerRepaint()
        # cache image should be cleared
        self.assertTrue(cache.cacheImage('xxx').isNull())
        self.assertFalse(cache.hasCacheImage('xxx'))
        QgsProject.instance().removeMapLayer(layer.id())

    def testRequestRepaintMultiple(self):
        """ test requesting repaint with multiple dependent layers """
        layer1 = QgsVectorLayer("Point?field=fldtxt:string",
                                "layer1", "memory")
        layer2 = QgsVectorLayer("Point?field=fldtxt:string",
                                "layer2", "memory")
        QgsProject.instance().addMapLayers([layer1, layer2])
        self.assertTrue(layer1.isValid())
        self.assertTrue(layer2.isValid())

        # add image to cache - no dependent layers
        cache = QgsMapRendererCache()
        im1 = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('nolayer', im1)
        self.assertFalse(cache.cacheImage('nolayer').isNull())
        self.assertTrue(cache.hasCacheImage('nolayer'))

        # trigger repaint on layer
        layer1.triggerRepaint()
        layer1.triggerRepaint() # do this a couple of times - we don't want errors due to multiple disconnects, etc
        layer2.triggerRepaint()
        layer2.triggerRepaint()
        # cache image should still exist - it's not dependent on layers
        self.assertFalse(cache.cacheImage('nolayer').isNull())
        self.assertTrue(cache.hasCacheImage('nolayer'))

        # image depends on 1 layer
        im_l1 = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('im1', im_l1, [layer1])

        # image depends on 2 layers
        im_l1_l2 = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('im1_im2', im_l1_l2, [layer1, layer2])

        # image depends on 2nd layer alone
        im_l2 = QImage(200, 200, QImage.Format_RGB32)
        cache.setCacheImage('im2', im_l2, [layer2])

        self.assertFalse(cache.cacheImage('im1').isNull())
        self.assertTrue(cache.hasCacheImage('im1'))
        self.assertFalse(cache.cacheImage('im1_im2').isNull())
        self.assertTrue(cache.hasCacheImage('im1_im2'))
        self.assertFalse(cache.cacheImage('im2').isNull())
        self.assertTrue(cache.hasCacheImage('im2'))

        # trigger repaint layer 1 (check twice - don't want disconnect errors)
        for i in range(2):
            layer1.triggerRepaint()
            #should be cleared
            self.assertTrue(cache.cacheImage('im1').isNull())
            self.assertFalse(cache.hasCacheImage('im1'))
            self.assertTrue(cache.cacheImage('im1_im2').isNull())
            self.assertFalse(cache.hasCacheImage('im1_im2'))
            # should be retained
            self.assertTrue(cache.hasCacheImage('im2'))
            self.assertFalse(cache.cacheImage('im2').isNull())
            self.assertEqual(cache.cacheImage('im2'), im_l2)
            self.assertTrue(cache.hasCacheImage('nolayer'))
            self.assertFalse(cache.cacheImage('nolayer').isNull())
            self.assertEqual(cache.cacheImage('nolayer'), im1)

        # trigger repaint layer 2
        for i in range(2):
            layer2.triggerRepaint()
            #should be cleared
            self.assertFalse(cache.hasCacheImage('im1'))
            self.assertTrue(cache.cacheImage('im1').isNull())
            self.assertFalse(cache.hasCacheImage('im1_im2'))
            self.assertTrue(cache.cacheImage('im1_im2').isNull())
            self.assertFalse(cache.hasCacheImage('im2'))
            self.assertTrue(cache.cacheImage('im2').isNull())
            # should be retained
            self.assertTrue(cache.hasCacheImage('nolayer'))
            self.assertFalse(cache.cacheImage('nolayer').isNull())
            self.assertEqual(cache.cacheImage('nolayer'), im1)


if __name__ == '__main__':
    unittest.main()
