# -*- coding: utf-8 -*-
"""QGIS Unit tests for QgsVectorLayer.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = 'Tim Sutton'
__date__ = '20/08/2012'
__copyright__ = 'Copyright 2012, The QGIS Project'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import qgis  # NOQA

import os

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QPainter
from qgis.PyQt.QtXml import (QDomDocument, QDomElement)

from qgis.core import (Qgis,
                       QgsWkbTypes,
                       QgsVectorLayer,
                       QgsRectangle,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsGeometry,
                       QgsPoint,
                       QgsField,
                       QgsFieldConstraints,
                       QgsFields,
                       QgsVectorLayerJoinInfo,
                       QgsSymbol,
                       QgsSingleSymbolRenderer,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
                       QgsUnitTypes,
                       QgsAggregateCalculator,
                       QgsPointV2,
                       QgsExpressionContext,
                       QgsExpressionContextScope,
                       QgsExpressionContextUtils)
from qgis.testing import start_app, unittest
from utilities import unitTestDataPath
start_app()


def createEmptyLayer():
    layer = QgsVectorLayer("Point", "addfeat", "memory")
    assert layer.pendingFeatureCount() == 0
    return layer


def createEmptyLayerWithFields():
    layer = QgsVectorLayer("Point?field=fldtxt:string&field=fldint:integer", "addfeat", "memory")
    assert layer.pendingFeatureCount() == 0
    return layer


def createLayerWithOnePoint():
    layer = QgsVectorLayer("Point?field=fldtxt:string&field=fldint:integer",
                           "addfeat", "memory")
    pr = layer.dataProvider()
    f = QgsFeature()
    f.setAttributes(["test", 123])
    f.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
    assert pr.addFeatures([f])
    assert layer.pendingFeatureCount() == 1
    return layer


def createLayerWithTwoPoints():
    layer = QgsVectorLayer("Point?field=fldtxt:string&field=fldint:integer",
                           "addfeat", "memory")
    pr = layer.dataProvider()
    f = QgsFeature()
    f.setAttributes(["test", 123])
    f.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
    f2 = QgsFeature()
    f2.setAttributes(["test2", 457])
    f2.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
    assert pr.addFeatures([f, f2])
    assert layer.pendingFeatureCount() == 2
    return layer


def createLayerWithFivePoints():
    layer = QgsVectorLayer("Point?field=fldtxt:string&field=fldint:integer",
                           "addfeat", "memory")
    pr = layer.dataProvider()
    f = QgsFeature()
    f.setAttributes(["test", 123])
    f.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
    f2 = QgsFeature()
    f2.setAttributes(["test2", 457])
    f2.setGeometry(QgsGeometry.fromPoint(QgsPoint(200, 200)))
    f3 = QgsFeature()
    f3.setAttributes(["test2", 888])
    f3.setGeometry(QgsGeometry.fromPoint(QgsPoint(300, 200)))
    f4 = QgsFeature()
    f4.setAttributes(["test3", -1])
    f4.setGeometry(QgsGeometry.fromPoint(QgsPoint(400, 300)))
    f5 = QgsFeature()
    f5.setAttributes(["test4", 0])
    f5.setGeometry(QgsGeometry.fromPoint(QgsPoint(0, 0)))
    assert pr.addFeatures([f, f2, f3, f4, f5])
    assert layer.featureCount() == 5
    return layer


def createJoinLayer():
    joinLayer = QgsVectorLayer(
        "Point?field=x:string&field=y:integer&field=z:integer",
        "joinlayer", "memory")
    pr = joinLayer.dataProvider()
    f1 = QgsFeature()
    f1.setAttributes(["foo", 123, 321])
    f1.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 1)))
    f2 = QgsFeature()
    f2.setAttributes(["bar", 456, 654])
    f2.setGeometry(QgsGeometry.fromPoint(QgsPoint(2, 2)))
    f3 = QgsFeature()
    f3.setAttributes(["qar", 457, 111])
    f3.setGeometry(QgsGeometry.fromPoint(QgsPoint(2, 2)))
    f4 = QgsFeature()
    f4.setAttributes(["a", 458, 19])
    f4.setGeometry(QgsGeometry.fromPoint(QgsPoint(2, 2)))
    assert pr.addFeatures([f1, f2, f3, f4])
    assert joinLayer.pendingFeatureCount() == 4
    return joinLayer


def dumpFeature(f):
    print("--- FEATURE DUMP ---")
    print(("valid: %d   | id: %d" % (f.isValid(), f.id())))
    geom = f.geometry()
    if geom:
        print(("geometry wkb: %d" % geom.wkbType()))
    else:
        print("no geometry")
    print(("attrs: %s" % str(f.attributes())))


def formatAttributes(attrs):
    return repr([str(a) for a in attrs])


def dumpEditBuffer(layer):
    editBuffer = layer.editBuffer()
    if not editBuffer:
        print("NO EDITING!")
        return
    print("ADDED:")
    for fid, f in editBuffer.addedFeatures().items():
        print(("%d: %s | %s" % (
            f.id(), formatAttributes(f.attributes()),
            f.geometry().exportToWkt())))
    print("CHANGED GEOM:")
    for fid, geom in editBuffer.changedGeometries().items():
        print(("%d | %s" % (f.id(), f.geometry().exportToWkt())))


class TestQgsVectorLayer(unittest.TestCase):

    def test_FeatureCount(self):
        myPath = os.path.join(unitTestDataPath(), 'lines.shp')
        myLayer = QgsVectorLayer(myPath, 'Lines', 'ogr')
        myCount = myLayer.featureCount()
        self.assertEqual(myCount, 6)

    # ADD FEATURE

    def test_AddFeature(self):
        layer = createEmptyLayerWithFields()
        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 2)))

        def checkAfter():
            self.assertEqual(layer.pendingFeatureCount(), 1)

            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(1, 2))

            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2.geometry().asPoint(), QgsPoint(1, 2))

        def checkBefore():
            self.assertEqual(layer.pendingFeatureCount(), 0)

            # check select+nextFeature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        checkBefore()

        # try to add feature without editing mode
        self.assertFalse(layer.addFeature(feat))

        # add feature
        layer.startEditing()

        # try adding feature with incorrect number of fields
        bad_feature = QgsFeature()
        self.assertFalse(layer.addFeature(bad_feature))

        # add good feature
        self.assertTrue(layer.addFeature(feat))

        checkAfter()
        self.assertEqual(layer.dataProvider().featureCount(), 0)

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())

        checkAfter()
        self.assertEqual(layer.dataProvider().featureCount(), 1)

    # ADD FEATURES

    def test_AddFeatures(self):
        layer = createEmptyLayerWithFields()
        feat1 = QgsFeature(layer.fields())
        feat1.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 2)))
        feat2 = QgsFeature(layer.fields())
        feat2.setGeometry(QgsGeometry.fromPoint(QgsPoint(11, 12)))

        def checkAfter():
            self.assertEqual(layer.pendingFeatureCount(), 2)

            # check select+nextFeature
            it = layer.getFeatures()
            f1 = next(it)
            self.assertEqual(f1.geometry().asPoint(), QgsPoint(1, 2))
            f2 = next(it)
            self.assertEqual(f2.geometry().asPoint(), QgsPoint(11, 12))

            # check feature at id
            f1_1 = next(layer.getFeatures(QgsFeatureRequest(f1.id())))
            self.assertEqual(f1_1.geometry().asPoint(), QgsPoint(1, 2))
            f2_1 = next(layer.getFeatures(QgsFeatureRequest(f2.id())))
            self.assertEqual(f2_1.geometry().asPoint(), QgsPoint(11, 12))

        def checkBefore():
            self.assertEqual(layer.pendingFeatureCount(), 0)

            # check select+nextFeature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        checkBefore()

        # try to add feature without editing mode
        self.assertFalse(layer.addFeatures([feat1, feat2]))

        # add feature
        layer.startEditing()

        # try adding feature with incorrect number of fields
        bad_feature = QgsFeature()
        self.assertFalse(layer.addFeatures([bad_feature]))

        # add good features
        self.assertTrue(layer.addFeatures([feat1, feat2]))

        checkAfter()
        self.assertEqual(layer.dataProvider().featureCount(), 0)

        # now try undo/redo
        layer.undoStack().undo()
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())

        checkAfter()
        self.assertEqual(layer.dataProvider().featureCount(), 2)
    # DELETE FEATURE

    def test_DeleteFeature(self):
        layer = createLayerWithOnePoint()
        fid = 1

        def checkAfter():
            self.assertEqual(layer.pendingFeatureCount(), 0)

            # check select+nextFeature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

            # check feature at id
            with self.assertRaises(StopIteration):
                next(layer.getFeatures(QgsFeatureRequest(fid)))

        def checkBefore():
            self.assertEqual(layer.pendingFeatureCount(), 1)

            # check select+nextFeature
            fi = layer.getFeatures()
            f = next(fi)
            self.assertEqual(f.geometry().asPoint(), QgsPoint(100, 200))
            with self.assertRaises(StopIteration):
                next(fi)

            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(fid)))
            self.assertEqual(f2.id(), fid)

        checkBefore()

        # try to delete feature without editing mode
        self.assertFalse(layer.deleteFeature(fid))

        # delete feature
        layer.startEditing()
        self.assertTrue(layer.deleteFeature(fid))

        checkAfter()

        # make sure calling it twice does not work
        self.assertFalse(layer.deleteFeature(fid))

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertEqual(layer.dataProvider().featureCount(), 1)

        self.assertTrue(layer.commitChanges())

        checkAfter()
        self.assertEqual(layer.dataProvider().featureCount(), 0)

    def test_DeleteFeatureAfterAddFeature(self):

        layer = createEmptyLayer()
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 2)))

        def checkBefore():
            self.assertEqual(layer.pendingFeatureCount(), 0)

            # check select+nextFeature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        def checkAfter1():
            self.assertEqual(layer.pendingFeatureCount(), 1)

        def checkAfter2():
            checkBefore()  # should be the same state: no features

        checkBefore()

        # add feature
        layer.startEditing()
        self.assertTrue(layer.addFeature(feat))
        checkAfter1()
        fid = feat.id()
        self.assertTrue(layer.deleteFeature(fid))
        checkAfter2()

        # now try undo/redo
        layer.undoStack().undo()
        checkAfter1()
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter1()
        layer.undoStack().redo()
        checkAfter2()

        self.assertTrue(layer.commitChanges())
        checkAfter2()

        self.assertEqual(layer.dataProvider().featureCount(), 0)

    # CHANGE ATTRIBUTE

    def test_ChangeAttribute(self):
        layer = createLayerWithOnePoint()
        fid = 1

        def checkAfter():
            # check select+nextFeature
            fi = layer.getFeatures()
            f = next(fi)
            self.assertEqual(f[0], "good")

            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2[0], "good")

        def checkBefore():
            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f[0], "test")

        checkBefore()

        # try to change attribute without editing mode
        self.assertFalse(layer.changeAttributeValue(fid, 0, "good"))

        # change attribute
        layer.startEditing()
        self.assertTrue(layer.changeAttributeValue(fid, 0, "good"))

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())
        checkAfter()

    def test_ChangeAttributeAfterAddFeature(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().deleteFeatures([1])  # no need for this feature

        newF = QgsFeature()
        newF.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 1)))
        newF.setAttributes(["hello", 42])

        def checkAfter():
            self.assertEqual(len(layer.pendingFields()), 2)
            # check feature
            fi = layer.getFeatures()
            f = next(fi)
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "hello")
            self.assertEqual(attrs[1], 12)

            with self.assertRaises(StopIteration):
                next(fi)

            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2[0], "hello")
            self.assertEqual(f2[1], 12)

        def checkBefore():
            # check feature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        checkBefore()

        layer.startEditing()
        layer.beginEditCommand("AddFeature + ChangeAttribute")
        self.assertTrue(layer.addFeature(newF))
        self.assertTrue(layer.changeAttributeValue(newF.id(), 1, 12))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())
        checkAfter()

        # print "COMMIT ERRORS:"
        # for item in list(layer.commitErrors()): print item

    # CHANGE GEOMETRY

    def test_ChangeGeometry(self):
        layer = createLayerWithOnePoint()
        fid = 1

        def checkAfter():
            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(300, 400))
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2.geometry().asPoint(), QgsPoint(300, 400))

        def checkBefore():
            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(100, 200))

        # try to change geometry without editing mode
        self.assertFalse(layer.changeGeometry(fid, QgsGeometry.fromPoint(QgsPoint(300, 400))))

        checkBefore()

        # change geometry
        layer.startEditing()
        layer.beginEditCommand("ChangeGeometry")
        self.assertTrue(layer.changeGeometry(fid, QgsGeometry.fromPoint(QgsPoint(300, 400))))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())
        checkAfter()

    def test_ChangeGeometryAfterChangeAttribute(self):
        layer = createLayerWithOnePoint()
        fid = 1

        def checkAfter():
            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(300, 400))
            self.assertEqual(f[0], "changed")
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2.geometry().asPoint(), QgsPoint(300, 400))
            self.assertEqual(f2[0], "changed")

        def checkBefore():
            # check select+nextFeature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(100, 200))
            self.assertEqual(f[0], "test")

        checkBefore()

        # change geometry
        layer.startEditing()
        layer.beginEditCommand("ChangeGeometry + ChangeAttribute")
        self.assertTrue(layer.changeAttributeValue(fid, 0, "changed"))
        self.assertTrue(layer.changeGeometry(fid, QgsGeometry.fromPoint(QgsPoint(300, 400))))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())
        checkAfter()

    def test_ChangeGeometryAfterAddFeature(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().deleteFeatures([1])  # no need for this feature

        newF = QgsFeature()
        newF.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 1)))
        newF.setAttributes(["hello", 42])

        def checkAfter():
            self.assertEqual(len(layer.pendingFields()), 2)
            # check feature
            f = next(layer.getFeatures())
            self.assertEqual(f.geometry().asPoint(), QgsPoint(2, 2))
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2.geometry().asPoint(), QgsPoint(2, 2))

        def checkBefore():
            # check feature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        checkBefore()

        layer.startEditing()
        layer.beginEditCommand("AddFeature+ChangeGeometry")
        self.assertTrue(layer.addFeature(newF))
        self.assertTrue(layer.changeGeometry(newF.id(), QgsGeometry.fromPoint(QgsPoint(2, 2))))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        self.assertTrue(layer.commitChanges())
        checkAfter()

        # print "COMMIT ERRORS:"
        # for item in list(layer.commitErrors()): print item

    # ADD ATTRIBUTE

    def test_AddAttribute(self):
        layer = createLayerWithOnePoint()
        fld1 = QgsField("fld1", QVariant.Int, "integer")
        #fld2 = QgsField("fld2", QVariant.Int, "integer")

        def checkBefore():
            # check fields
            flds = layer.pendingFields()
            self.assertEqual(len(flds), 2)
            self.assertEqual(flds[0].name(), "fldtxt")
            self.assertEqual(flds[1].name(), "fldint")

            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "test")
            self.assertEqual(attrs[1], 123)

        def checkAfter():
            # check fields
            flds = layer.pendingFields()
            self.assertEqual(len(flds), 3)
            self.assertEqual(flds[0].name(), "fldtxt")
            self.assertEqual(flds[1].name(), "fldint")
            self.assertEqual(flds[2].name(), "fld1")

            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 3)
            self.assertEqual(attrs[0], "test")
            self.assertEqual(attrs[1], 123)
            self.assertTrue(attrs[2] is None)

            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2[0], "test")
            self.assertEqual(f2[1], 123)
            self.assertTrue(f2[2] is None)

        # for nt in layer.dataProvider().nativeTypes():
        #    print (nt.mTypeDesc, nt.mTypeName, nt.mType, nt.mMinLen,
        #          nt.mMaxLen, nt.mMinPrec, nt.mMaxPrec)
        self.assertTrue(layer.dataProvider().supportedType(fld1))

        # without editing mode
        self.assertFalse(layer.addAttribute(fld1))

        layer.startEditing()

        checkBefore()

        self.assertTrue(layer.addAttribute(fld1))
        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        layer.commitChanges()
        checkAfter()

    def test_AddAttributeAfterAddFeature(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().deleteFeatures([1])  # no need for this feature

        newF = QgsFeature()
        newF.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 1)))
        newF.setAttributes(["hello", 42])

        fld1 = QgsField("fld1", QVariant.Int, "integer")

        def checkBefore():
            self.assertEqual(len(layer.pendingFields()), 2)
            # check feature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        def checkAfter():
            self.assertEqual(len(layer.pendingFields()), 3)
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 3)
            self.assertEqual(attrs[0], "hello")
            self.assertEqual(attrs[1], 42)
            self.assertTrue(attrs[2] is None)
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(f2[0], "hello")
            self.assertEqual(f2[1], 42)
            self.assertTrue(f2[2] is None)

        layer.startEditing()

        checkBefore()

        layer.beginEditCommand("AddFeature + AddAttribute")
        self.assertTrue(layer.addFeature(newF))
        self.assertTrue(layer.addAttribute(fld1))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter()

        layer.commitChanges()
        checkAfter()

        # print "COMMIT ERRORS:"
        # for item in list(layer.commitErrors()): print item

    def test_AddAttributeAfterChangeValue(self):
        pass  # not interesting to test...?

    def test_AddAttributeAfterDeleteAttribute(self):
        pass  # maybe it would be good to test

    # DELETE ATTRIBUTE

    def test_DeleteAttribute(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().addAttributes(
            [QgsField("flddouble", QVariant.Double, "double")])
        layer.dataProvider().changeAttributeValues(
            {1: {2: 5.5}})

        # without editing mode
        self.assertFalse(layer.deleteAttribute(0))

        def checkBefore():
            flds = layer.pendingFields()
            self.assertEqual(len(flds), 3)
            self.assertEqual(flds[0].name(), "fldtxt")
            self.assertEqual(flds[1].name(), "fldint")
            self.assertEqual(flds[2].name(), "flddouble")

            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 3)
            self.assertEqual(attrs[0], "test")
            self.assertEqual(attrs[1], 123)
            self.assertEqual(attrs[2], 5.5)

        layer.startEditing()

        checkBefore()

        self.assertTrue(layer.deleteAttribute(0))

        def checkAfterOneDelete():
            flds = layer.pendingFields()
            # for fld in flds: print "FLD", fld.name()
            self.assertEqual(len(flds), 2)
            self.assertEqual(flds[0].name(), "fldint")
            self.assertEqual(flds[1].name(), "flddouble")
            self.assertEqual(layer.pendingAllAttributesList(), [0, 1])

            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], 123)
            self.assertEqual(attrs[1], 5.5)

        checkAfterOneDelete()

        # delete last attribute
        self.assertTrue(layer.deleteAttribute(0))

        def checkAfterTwoDeletes():
            self.assertEqual(layer.pendingAllAttributesList(), [0])
            flds = layer.pendingFields()
            # for fld in flds: print "FLD", fld.name()
            self.assertEqual(len(flds), 1)
            self.assertEqual(flds[0].name(), "flddouble")

            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 1)
            self.assertEqual(attrs[0], 5.5)
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(len(f2.attributes()), 1)
            self.assertEqual(f2[0], 5.5)

        checkAfterTwoDeletes()
        layer.undoStack().undo()
        checkAfterOneDelete()
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfterOneDelete()
        layer.undoStack().redo()
        checkAfterTwoDeletes()

        self.assertTrue(layer.commitChanges())  # COMMIT!
        checkAfterTwoDeletes()

    def test_DeleteAttributeAfterAddAttribute(self):
        layer = createLayerWithOnePoint()
        fld1 = QgsField("fld1", QVariant.Int, "integer")

        def checkAfter():  # layer should be unchanged
            flds = layer.pendingFields()
            self.assertEqual(len(flds), 2)
            self.assertEqual(flds[0].name(), "fldtxt")
            self.assertEqual(flds[1].name(), "fldint")

            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "test")
            self.assertEqual(attrs[1], 123)
            # check feature at id
            f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
            self.assertEqual(len(f2.attributes()), 2)
            self.assertEqual(f2[0], "test")
            self.assertEqual(f2[1], 123)

        checkAfter()

        layer.startEditing()

        layer.beginEditCommand("AddAttribute + DeleteAttribute")
        self.assertTrue(layer.addAttribute(fld1))
        self.assertTrue(layer.deleteAttribute(2))
        layer.endEditCommand()

        checkAfter()

        # now try undo/redo
        layer.undoStack().undo()
        checkAfter()
        layer.undoStack().redo()
        checkAfter()

        layer.commitChanges()
        checkAfter()

    def test_DeleteAttributeAfterAddFeature(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().deleteFeatures([1])  # no need for this feature

        newF = QgsFeature()
        newF.setGeometry(QgsGeometry.fromPoint(QgsPoint(1, 1)))
        newF.setAttributes(["hello", 42])

        def checkBefore():
            self.assertEqual(len(layer.pendingFields()), 2)
            # check feature
            with self.assertRaises(StopIteration):
                next(layer.getFeatures())

        def checkAfter1():
            self.assertEqual(len(layer.pendingFields()), 2)
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "hello")
            self.assertEqual(attrs[1], 42)

        def checkAfter2():
            self.assertEqual(len(layer.pendingFields()), 1)
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 1)
            self.assertEqual(attrs[0], 42)

        layer.startEditing()

        checkBefore()

        layer.addFeature(newF)
        checkAfter1()
        layer.deleteAttribute(0)
        checkAfter2()

        # now try undo/redo
        layer.undoStack().undo()
        checkAfter1()
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter1()
        layer.undoStack().redo()
        checkAfter2()

        layer.commitChanges()
        checkAfter2()

    def test_DeleteAttributeAfterChangeValue(self):
        layer = createLayerWithOnePoint()

        def checkBefore():
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "test")
            self.assertEqual(attrs[1], 123)

        def checkAfter1():
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 2)
            self.assertEqual(attrs[0], "changed")
            self.assertEqual(attrs[1], 123)

        def checkAfter2():
            # check feature
            f = next(layer.getFeatures())
            attrs = f.attributes()
            self.assertEqual(len(attrs), 1)
            self.assertEqual(attrs[0], 123)

        layer.startEditing()

        checkBefore()

        self.assertTrue(layer.changeAttributeValue(1, 0, "changed"))
        checkAfter1()
        self.assertTrue(layer.deleteAttribute(0))
        checkAfter2()

        # now try undo/redo
        layer.undoStack().undo()
        checkAfter1()
        layer.undoStack().undo()
        checkBefore()
        layer.undoStack().redo()
        checkAfter1()
        layer.undoStack().redo()
        checkAfter2()

        layer.commitChanges()
        checkAfter2()

    # RENAME ATTRIBUTE

    def test_RenameAttribute(self):
        layer = createLayerWithOnePoint()

        # without editing mode
        self.assertFalse(layer.renameAttribute(0, 'renamed'))

        def checkFieldNames(names):
            flds = layer.fields()
            f = next(layer.getFeatures())
            self.assertEqual(flds.count(), len(names))
            self.assertEqual(f.fields().count(), len(names))

            for idx, expected_name in enumerate(names):
                self.assertEqual(flds[idx].name(), expected_name)
                self.assertEqual(f.fields().at(idx).name(), expected_name)

        layer.startEditing()

        checkFieldNames(['fldtxt', 'fldint'])

        self.assertFalse(layer.renameAttribute(-1, 'fldtxt2'))
        self.assertFalse(layer.renameAttribute(10, 'fldtxt2'))
        self.assertFalse(layer.renameAttribute(0, 'fldint')) # duplicate name

        self.assertTrue(layer.renameAttribute(0, 'fldtxt2'))
        checkFieldNames(['fldtxt2', 'fldint'])

        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt2', 'fldint'])

        # change two fields
        self.assertTrue(layer.renameAttribute(1, 'fldint2'))
        checkFieldNames(['fldtxt2', 'fldint2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt2', 'fldint'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt2', 'fldint'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt2', 'fldint2'])

        # two renames
        self.assertTrue(layer.renameAttribute(0, 'fldtxt3'))
        checkFieldNames(['fldtxt3', 'fldint2'])
        self.assertTrue(layer.renameAttribute(0, 'fldtxt4'))
        checkFieldNames(['fldtxt4', 'fldint2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt3', 'fldint2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt2', 'fldint2'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt3', 'fldint2'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt4', 'fldint2'])

    def test_RenameAttributeAfterAdd(self):
        layer = createLayerWithOnePoint()

        def checkFieldNames(names):
            flds = layer.fields()
            f = next(layer.getFeatures())
            self.assertEqual(flds.count(), len(names))
            self.assertEqual(f.fields().count(), len(names))

            for idx, expected_name in enumerate(names):
                self.assertEqual(flds[idx].name(), expected_name)
                self.assertEqual(f.fields().at(idx).name(), expected_name)

        layer.startEditing()

        checkFieldNames(['fldtxt', 'fldint'])
        self.assertTrue(layer.renameAttribute(1, 'fldint2'))
        checkFieldNames(['fldtxt', 'fldint2'])
        #add an attribute
        self.assertTrue(layer.addAttribute(QgsField("flddouble", QVariant.Double, "double")))
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble'])
        # rename it
        self.assertTrue(layer.renameAttribute(2, 'flddouble2'))
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2'])
        self.assertTrue(layer.addAttribute(QgsField("flddate", QVariant.Date, "date")))
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2', 'flddate'])
        self.assertTrue(layer.renameAttribute(2, 'flddouble3'))
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble3', 'flddate'])
        self.assertTrue(layer.renameAttribute(3, 'flddate2'))
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble3', 'flddate2'])

        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble3', 'flddate'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2', 'flddate'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint'])

        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble2', 'flddate'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble3', 'flddate'])
        layer.undoStack().redo()
        checkFieldNames(['fldtxt', 'fldint2', 'flddouble3', 'flddate2'])

    def test_RenameAttributeAndDelete(self):
        layer = createLayerWithOnePoint()
        layer.dataProvider().addAttributes(
            [QgsField("flddouble", QVariant.Double, "double")])
        layer.updateFields()

        def checkFieldNames(names):
            flds = layer.fields()
            f = next(layer.getFeatures())
            self.assertEqual(flds.count(), len(names))
            self.assertEqual(f.fields().count(), len(names))

            for idx, expected_name in enumerate(names):
                self.assertEqual(flds[idx].name(), expected_name)
                self.assertEqual(f.fields().at(idx).name(), expected_name)

        layer.startEditing()

        checkFieldNames(['fldtxt', 'fldint', 'flddouble'])
        self.assertTrue(layer.renameAttribute(0, 'fldtxt2'))
        checkFieldNames(['fldtxt2', 'fldint', 'flddouble'])
        self.assertTrue(layer.renameAttribute(2, 'flddouble2'))
        checkFieldNames(['fldtxt2', 'fldint', 'flddouble2'])

        #delete an attribute
        self.assertTrue(layer.deleteAttribute(0))
        checkFieldNames(['fldint', 'flddouble2'])
        # rename remaining
        self.assertTrue(layer.renameAttribute(0, 'fldint2'))
        checkFieldNames(['fldint2', 'flddouble2'])
        self.assertTrue(layer.renameAttribute(1, 'flddouble3'))
        checkFieldNames(['fldint2', 'flddouble3'])
        #delete an attribute
        self.assertTrue(layer.deleteAttribute(0))
        checkFieldNames(['flddouble3'])
        self.assertTrue(layer.renameAttribute(0, 'flddouble4'))
        checkFieldNames(['flddouble4'])

        layer.undoStack().undo()
        checkFieldNames(['flddouble3'])
        layer.undoStack().undo()
        checkFieldNames(['fldint2', 'flddouble3'])
        layer.undoStack().undo()
        checkFieldNames(['fldint2', 'flddouble2'])
        layer.undoStack().undo()
        checkFieldNames(['fldint', 'flddouble2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt2', 'fldint', 'flddouble2'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt2', 'fldint', 'flddouble'])
        layer.undoStack().undo()
        checkFieldNames(['fldtxt', 'fldint', 'flddouble'])

        #layer.undoStack().redo()
        #checkFieldNames(['fldtxt2', 'fldint'])
        #layer.undoStack().redo()
        #checkFieldNames(['fldint'])

    def test_RenameExpressionField(self):
        layer = createLayerWithOnePoint()
        exp_field_idx = layer.addExpressionField('1+1', QgsField('math_is_hard', QVariant.Int))

        #rename and check
        self.assertTrue(layer.renameAttribute(exp_field_idx, 'renamed'))
        self.assertEqual(layer.fields()[exp_field_idx].name(), 'renamed')
        f = next(layer.getFeatures())
        self.assertEqual(f.fields()[exp_field_idx].name(), 'renamed')

    def test_fields(self):
        layer = createLayerWithOnePoint()

        flds = layer.pendingFields()
        self.assertEqual(flds.indexFromName("fldint"), 1)
        self.assertEqual(flds.indexFromName("fldXXX"), -1)

    def test_getFeatures(self):

        layer = createLayerWithOnePoint()

        f = QgsFeature()
        fi = layer.getFeatures()
        self.assertTrue(fi.nextFeature(f))
        self.assertTrue(f.isValid())
        self.assertEqual(f.id(), 1)
        self.assertEqual(f.geometry().asPoint(), QgsPoint(100, 200))
        self.assertEqual(f["fldtxt"], "test")
        self.assertEqual(f["fldint"], 123)

        self.assertFalse(fi.nextFeature(f))

        layer2 = createLayerWithFivePoints()

        # getFeature(fid)
        feat = layer2.getFeature(4)
        self.assertTrue(feat.isValid())
        self.assertEqual(feat['fldtxt'], 'test3')
        self.assertEqual(feat['fldint'], -1)
        feat = layer2.getFeature(10)
        self.assertFalse(feat.isValid())

        # getFeatures(expression)
        it = layer2.getFeatures("fldint <= 0")
        fids = [f.id() for f in it]
        self.assertEqual(set(fids), set([4, 5]))

        # getFeatures(fids)
        it = layer2.getFeatures([1, 2])
        fids = [f.id() for f in it]
        self.assertEqual(set(fids), set([1, 2]))

        # getFeatures(rect)
        it = layer2.getFeatures(QgsRectangle(99, 99, 201, 201))
        fids = [f.id() for f in it]
        self.assertEqual(set(fids), set([1, 2]))

    def test_join(self):

        joinLayer = createJoinLayer()
        joinLayer2 = createJoinLayer()
        QgsProject.instance().addMapLayers([joinLayer, joinLayer2])

        layer = createLayerWithOnePoint()

        join = QgsVectorLayerJoinInfo()
        join.setTargetFieldName("fldint")
        join.setJoinLayer(joinLayer)
        join.setJoinFieldName("y")
        join.setUsingMemoryCache(True)

        layer.addJoin(join)

        join2 = QgsVectorLayerJoinInfo()
        join2.setTargetFieldName("fldint")
        join2.setJoinLayer(joinLayer2)
        join2.setJoinFieldName("y")
        join2.setUsingMemoryCache(True)
        join2.setPrefix("custom-prefix_")

        layer.addJoin(join2)

        flds = layer.pendingFields()
        self.assertEqual(len(flds), 6)
        self.assertEqual(flds[2].name(), "joinlayer_x")
        self.assertEqual(flds[3].name(), "joinlayer_z")
        self.assertEqual(flds[4].name(), "custom-prefix_x")
        self.assertEqual(flds[5].name(), "custom-prefix_z")
        self.assertEqual(flds.fieldOrigin(0), QgsFields.OriginProvider)
        self.assertEqual(flds.fieldOrigin(2), QgsFields.OriginJoin)
        self.assertEqual(flds.fieldOrigin(3), QgsFields.OriginJoin)
        self.assertEqual(flds.fieldOriginIndex(0), 0)
        self.assertEqual(flds.fieldOriginIndex(2), 0)
        self.assertEqual(flds.fieldOriginIndex(3), 2)

        f = QgsFeature()
        fi = layer.getFeatures()
        self.assertTrue(fi.nextFeature(f))
        attrs = f.attributes()
        self.assertEqual(len(attrs), 6)
        self.assertEqual(attrs[0], "test")
        self.assertEqual(attrs[1], 123)
        self.assertEqual(attrs[2], "foo")
        self.assertEqual(attrs[3], 321)
        self.assertFalse(fi.nextFeature(f))

        f2 = next(layer.getFeatures(QgsFeatureRequest(f.id())))
        self.assertEqual(len(f2.attributes()), 6)
        self.assertEqual(f2[2], "foo")
        self.assertEqual(f2[3], 321)

    def test_JoinStats(self):
        """ test calculating min/max/uniqueValues on joined field """
        joinLayer = createJoinLayer()
        layer = createLayerWithTwoPoints()
        QgsProject.instance().addMapLayers([joinLayer, layer])

        join = QgsVectorLayerJoinInfo()
        join.setTargetFieldName("fldint")
        join.setJoinLayer(joinLayer)
        join.setJoinFieldName("y")
        join.setUsingMemoryCache(True)
        layer.addJoin(join)

        # stats on joined fields should only include values present by join
        self.assertEqual(layer.minimumValue(3), 111)
        self.assertEqual(layer.maximumValue(3), 321)
        self.assertEqual(set(layer.uniqueValues(3)), set([111, 321]))

    def testUniqueValue(self):
        """ test retrieving unique values """
        layer = createLayerWithFivePoints()

        # test layer with just provider features
        self.assertEqual(set(layer.uniqueValues(1)), set([123, 457, 888, -1, 0]))

        # add feature with new value
        layer.startEditing()
        f1 = QgsFeature()
        f1.setAttributes(["test2", 999])
        self.assertTrue(layer.addFeature(f1))

        # should be included in unique values
        self.assertEqual(set(layer.uniqueValues(1)), set([123, 457, 888, -1, 0, 999]))
        # add it again, should be no change
        f2 = QgsFeature()
        f2.setAttributes(["test2", 999])
        self.assertTrue(layer.addFeature(f1))
        self.assertEqual(set(layer.uniqueValues(1)), set([123, 457, 888, -1, 0, 999]))
        # add another feature
        f3 = QgsFeature()
        f3.setAttributes(["test2", 9999])
        self.assertTrue(layer.addFeature(f3))
        self.assertEqual(set(layer.uniqueValues(1)), set([123, 457, 888, -1, 0, 999, 9999]))

        # change an attribute value to a new unique value
        f = QgsFeature()
        f1_id = next(layer.getFeatures()).id()
        self.assertTrue(layer.changeAttributeValue(f1_id, 1, 481523))
        # note - this isn't 100% accurate, since 123 no longer exists - but it avoids looping through all features
        self.assertEqual(set(layer.uniqueValues(1)), set([123, 457, 888, -1, 0, 999, 9999, 481523]))

    def testUniqueStringsMatching(self):
        """ test retrieving unique strings matching subset """
        layer = QgsVectorLayer("Point?field=fldtxt:string", "addfeat", "memory")
        pr = layer.dataProvider()
        f = QgsFeature()
        f.setAttributes(["apple"])
        f2 = QgsFeature()
        f2.setAttributes(["orange"])
        f3 = QgsFeature()
        f3.setAttributes(["pear"])
        f4 = QgsFeature()
        f4.setAttributes(["BanaNa"])
        f5 = QgsFeature()
        f5.setAttributes(["ApriCot"])
        assert pr.addFeatures([f, f2, f3, f4, f5])
        assert layer.featureCount() == 5

        # test layer with just provider features
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'N')), set(['orange', 'BanaNa']))

        # add feature with new value
        layer.startEditing()
        f1 = QgsFeature()
        f1.setAttributes(["waterMelon"])
        self.assertTrue(layer.addFeature(f1))

        # should be included in unique values
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'N')), set(['orange', 'BanaNa', 'waterMelon']))
        # add it again, should be no change
        f2 = QgsFeature()
        f2.setAttributes(["waterMelon"])
        self.assertTrue(layer.addFeature(f1))
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'N')), set(['orange', 'BanaNa', 'waterMelon']))
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'aN')), set(['orange', 'BanaNa']))
        # add another feature
        f3 = QgsFeature()
        f3.setAttributes(["pineapple"])
        self.assertTrue(layer.addFeature(f3))
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'n')), set(['orange', 'BanaNa', 'waterMelon', 'pineapple']))

        # change an attribute value to a new unique value
        f = QgsFeature()
        f1_id = next(layer.getFeatures()).id()
        self.assertTrue(layer.changeAttributeValue(f1_id, 0, 'coconut'))
        # note - this isn't 100% accurate, since orange no longer exists - but it avoids looping through all features
        self.assertEqual(set(layer.uniqueStringsMatching(0, 'n')), set(['orange', 'BanaNa', 'waterMelon', 'pineapple', 'coconut']))

    def testMinValue(self):
        """ test retrieving minimum values """
        layer = createLayerWithFivePoints()

        # test layer with just provider features
        self.assertEqual(layer.minimumValue(1), -1)

        # add feature with new value
        layer.startEditing()
        f1 = QgsFeature()
        f1.setAttributes(["test2", -999])
        self.assertTrue(layer.addFeature(f1))

        # should be new minimum value
        self.assertEqual(layer.minimumValue(1), -999)
        # add it again, should be no change
        f2 = QgsFeature()
        f2.setAttributes(["test2", -999])
        self.assertTrue(layer.addFeature(f1))
        self.assertEqual(layer.minimumValue(1), -999)
        # add another feature
        f3 = QgsFeature()
        f3.setAttributes(["test2", -1000])
        self.assertTrue(layer.addFeature(f3))
        self.assertEqual(layer.minimumValue(1), -1000)

        # change an attribute value to a new minimum value
        f = QgsFeature()
        f1_id = next(layer.getFeatures()).id()
        self.assertTrue(layer.changeAttributeValue(f1_id, 1, -1001))
        self.assertEqual(layer.minimumValue(1), -1001)

    def testMaxValue(self):
        """ test retrieving maximum values """
        layer = createLayerWithFivePoints()

        # test layer with just provider features
        self.assertEqual(layer.maximumValue(1), 888)

        # add feature with new value
        layer.startEditing()
        f1 = QgsFeature()
        f1.setAttributes(["test2", 999])
        self.assertTrue(layer.addFeature(f1))

        # should be new maximum value
        self.assertEqual(layer.maximumValue(1), 999)
        # add it again, should be no change
        f2 = QgsFeature()
        f2.setAttributes(["test2", 999])
        self.assertTrue(layer.addFeature(f1))
        self.assertEqual(layer.maximumValue(1), 999)
        # add another feature
        f3 = QgsFeature()
        f3.setAttributes(["test2", 1000])
        self.assertTrue(layer.addFeature(f3))
        self.assertEqual(layer.maximumValue(1), 1000)

        # change an attribute value to a new maximum value
        f = QgsFeature()
        f1_id = next(layer.getFeatures()).id()
        self.assertTrue(layer.changeAttributeValue(f1_id, 1, 1001))
        self.assertEqual(layer.maximumValue(1), 1001)

    def test_InvalidOperations(self):
        layer = createLayerWithOnePoint()

        layer.startEditing()

        # ADD FEATURE

        newF1 = QgsFeature()
        self.assertFalse(layer.addFeature(newF1))  # need attributes like the layer has)

        # DELETE FEATURE

        self.assertFalse(layer.deleteFeature(-333))
        # we do not check for existence of the feature id if it's
        # not newly added feature
        #self.assertFalse(layer.deleteFeature(333))

        # CHANGE GEOMETRY

        self.assertFalse(layer.changeGeometry(
            -333, QgsGeometry.fromPoint(QgsPoint(1, 1))))

        # CHANGE VALUE

        self.assertFalse(layer.changeAttributeValue(-333, 0, 1))
        self.assertFalse(layer.changeAttributeValue(1, -1, 1))

        # ADD ATTRIBUTE

        self.assertFalse(layer.addAttribute(QgsField()))

        # DELETE ATTRIBUTE

        self.assertFalse(layer.deleteAttribute(-1))

    def onBlendModeChanged(self, mode):
        self.blendModeTest = mode

    def test_setBlendMode(self):
        layer = createLayerWithOnePoint()

        self.blendModeTest = 0
        layer.blendModeChanged.connect(self.onBlendModeChanged)
        layer.setBlendMode(QPainter.CompositionMode_Screen)

        self.assertEqual(self.blendModeTest, QPainter.CompositionMode_Screen)
        self.assertEqual(layer.blendMode(), QPainter.CompositionMode_Screen)

    def test_setFeatureBlendMode(self):
        layer = createLayerWithOnePoint()

        self.blendModeTest = 0
        layer.featureBlendModeChanged.connect(self.onBlendModeChanged)
        layer.setFeatureBlendMode(QPainter.CompositionMode_Screen)

        self.assertEqual(self.blendModeTest, QPainter.CompositionMode_Screen)
        self.assertEqual(layer.featureBlendMode(), QPainter.CompositionMode_Screen)

    def test_ExpressionField(self):
        layer = createLayerWithOnePoint()

        cnt = layer.pendingFields().count()

        idx = layer.addExpressionField('5', QgsField('test', QVariant.LongLong))

        fet = next(layer.getFeatures())
        self.assertEqual(fet[idx], 5)
        # check fields
        self.assertEqual(layer.fields().count(), cnt + 1)
        self.assertEqual(fet.fields(), layer.fields())

        # retrieve single feature and check fields
        fet = next(layer.getFeatures(QgsFeatureRequest().setFilterFid(1)))
        self.assertEqual(fet.fields(), layer.fields())

        layer.updateExpressionField(idx, '9')

        self.assertEqual(next(layer.getFeatures())[idx], 9)

        layer.removeExpressionField(idx)

        self.assertEqual(layer.pendingFields().count(), cnt)

    def test_ExpressionFieldEllipsoidLengthCalculation(self):
        #create a temporary layer
        temp_layer = QgsVectorLayer("LineString?crs=epsg:3111&field=pk:int", "vl", "memory")
        self.assertTrue(temp_layer.isValid())
        f1 = QgsFeature(temp_layer.dataProvider().fields(), 1)
        f1.setAttribute("pk", 1)
        f1.setGeometry(QgsGeometry.fromPolyline([QgsPoint(2484588, 2425722), QgsPoint(2482767, 2398853)]))
        temp_layer.dataProvider().addFeatures([f1])

        # set project CRS and ellipsoid
        srs = QgsCoordinateReferenceSystem(3111, QgsCoordinateReferenceSystem.EpsgCrsId)
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCRSProj4String", srs.toProj4())
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCRSID", srs.srsid())
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCrs", srs.authid())
        QgsProject.instance().writeEntry("Measure", "/Ellipsoid", "WGS84")
        QgsProject.instance().writeEntry("Measurement", "/DistanceUnits", QgsUnitTypes.encodeUnit(QgsUnitTypes.DistanceMeters))

        idx = temp_layer.addExpressionField('$length', QgsField('length', QVariant.Double))  # NOQA

        # check value
        f = next(temp_layer.getFeatures())
        expected = 26932.156
        self.assertAlmostEqual(f['length'], expected, 3)

        # change project length unit, check calculation respects unit
        QgsProject.instance().writeEntry("Measurement", "/DistanceUnits", QgsUnitTypes.encodeUnit(QgsUnitTypes.DistanceFeet))
        f = next(temp_layer.getFeatures())
        expected = 88360.0918635
        self.assertAlmostEqual(f['length'], expected, 3)

    def test_ExpressionFieldEllipsoidAreaCalculation(self):
        #create a temporary layer
        temp_layer = QgsVectorLayer("Polygon?crs=epsg:3111&field=pk:int", "vl", "memory")
        self.assertTrue(temp_layer.isValid())
        f1 = QgsFeature(temp_layer.dataProvider().fields(), 1)
        f1.setAttribute("pk", 1)
        f1.setGeometry(QgsGeometry.fromPolygon([[QgsPoint(2484588, 2425722), QgsPoint(2482767, 2398853), QgsPoint(2520109, 2397715), QgsPoint(2520792, 2425494), QgsPoint(2484588, 2425722)]]))
        temp_layer.dataProvider().addFeatures([f1])

        # set project CRS and ellipsoid
        srs = QgsCoordinateReferenceSystem(3111, QgsCoordinateReferenceSystem.EpsgCrsId)
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCRSProj4String", srs.toProj4())
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCRSID", srs.srsid())
        QgsProject.instance().writeEntry("SpatialRefSys", "/ProjectCrs", srs.authid())
        QgsProject.instance().writeEntry("Measure", "/Ellipsoid", "WGS84")
        QgsProject.instance().writeEntry("Measurement", "/AreaUnits", QgsUnitTypes.encodeUnit(QgsUnitTypes.AreaSquareMeters))

        idx = temp_layer.addExpressionField('$area', QgsField('area', QVariant.Double))  # NOQA

        # check value
        f = next(temp_layer.getFeatures())
        expected = 1009089817.0
        self.assertAlmostEqual(f['area'], expected, delta=1.0)

        # change project area unit, check calculation respects unit
        QgsProject.instance().writeEntry("Measurement", "/AreaUnits", QgsUnitTypes.encodeUnit(QgsUnitTypes.AreaSquareMiles))
        f = next(temp_layer.getFeatures())
        expected = 389.6117565069
        self.assertAlmostEqual(f['area'], expected, 3)

    def test_ExpressionFilter(self):
        layer = createLayerWithOnePoint()

        idx = layer.addExpressionField('5', QgsField('test', QVariant.LongLong))  # NOQA

        features = layer.getFeatures(QgsFeatureRequest().setFilterExpression('"test" = 6'))

        assert(len(list(features)) == 0)

        features = layer.getFeatures(QgsFeatureRequest().setFilterExpression('"test" = 5'))

        assert(len(list(features)) == 1)

    def testSelectByIds(self):
        """ Test selecting by ID"""
        layer = QgsVectorLayer(os.path.join(unitTestDataPath(), 'points.shp'), 'Points', 'ogr')

        # SetSelection
        layer.selectByIds([1, 3, 5, 7], QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 3, 5, 7]))
        # check that existing selection is cleared
        layer.selectByIds([2, 4, 6], QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 4, 6]))

        # AddToSelection
        layer.selectByIds([3, 5], QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 4, 5, 6]))
        layer.selectByIds([1], QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 2, 3, 4, 5, 6]))

        # IntersectSelection
        layer.selectByIds([1, 3, 5, 6], QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 3, 5, 6]))
        layer.selectByIds([1, 2, 5, 6], QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 5, 6]))

        # RemoveFromSelection
        layer.selectByIds([2, 6, 7], QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 5]))
        layer.selectByIds([1, 5], QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([]))

    def testSelectByExpression(self):
        """ Test selecting by expression """
        layer = QgsVectorLayer(os.path.join(unitTestDataPath(), 'points.shp'), 'Points', 'ogr')

        # SetSelection
        layer.selectByExpression('"Class"=\'B52\' and "Heading" > 10 and "Heading" <70', QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([10, 11]))
        # check that existing selection is cleared
        layer.selectByExpression('"Class"=\'Biplane\'', QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([1, 5, 6, 7, 8]))
        # SetSelection no matching
        layer.selectByExpression('"Class"=\'A380\'', QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([]))

        # AddToSelection
        layer.selectByExpression('"Importance"=3', QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([0, 2, 3, 4, 14]))
        layer.selectByExpression('"Importance"=4', QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([0, 2, 3, 4, 13, 14]))

        # IntersectSelection
        layer.selectByExpression('"Heading"<100', QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([0, 2, 3, 4]))
        layer.selectByExpression('"Cabin Crew"=1', QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3]))

        # RemoveFromSelection
        layer.selectByExpression('"Heading"=85', QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([3]))
        layer.selectByExpression('"Heading"=95', QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([]))

    def testSelectByRect(self):
        """ Test selecting by rectangle """
        layer = QgsVectorLayer(os.path.join(unitTestDataPath(), 'points.shp'), 'Points', 'ogr')

        # SetSelection
        layer.selectByRect(QgsRectangle(-112, 30, -94, 45), QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 7, 10, 11, 15]))
        # check that existing selection is cleared
        layer.selectByRect(QgsRectangle(-112, 30, -94, 37), QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 10, 15]))
        # SetSelection no matching
        layer.selectByRect(QgsRectangle(112, 30, 115, 45), QgsVectorLayer.SetSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([]))

        # AddToSelection
        layer.selectByRect(QgsRectangle(-112, 30, -94, 37), QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 10, 15]))
        layer.selectByRect(QgsRectangle(-112, 37, -94, 45), QgsVectorLayer.AddToSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 7, 10, 11, 15]))

        # IntersectSelection
        layer.selectByRect(QgsRectangle(-112, 30, -94, 37), QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 3, 10, 15]))
        layer.selectByIds([2, 10, 13])
        layer.selectByRect(QgsRectangle(-112, 30, -94, 37), QgsVectorLayer.IntersectSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([2, 10]))

        # RemoveFromSelection
        layer.selectByRect(QgsRectangle(-112, 30, -94, 45), QgsVectorLayer.SetSelection)
        layer.selectByRect(QgsRectangle(-112, 30, -94, 37), QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([7, 11]))
        layer.selectByRect(QgsRectangle(-112, 30, -94, 45), QgsVectorLayer.RemoveFromSelection)
        self.assertEqual(set(layer.selectedFeatureIds()), set([]))

    def testAggregate(self):
        """ Test aggregate calculation """
        layer = QgsVectorLayer("Point?field=fldint:integer", "layer", "memory")
        pr = layer.dataProvider()

        int_values = [4, 2, 3, 2, 5, None, 8]
        features = []
        for i in int_values:
            f = QgsFeature()
            f.setFields(layer.fields())
            f.setAttributes([i])
            features.append(f)
        assert pr.addFeatures(features)

        tests = [[QgsAggregateCalculator.Count, 6],
                 [QgsAggregateCalculator.Sum, 24],
                 [QgsAggregateCalculator.Mean, 4],
                 [QgsAggregateCalculator.StDev, 2.0816],
                 [QgsAggregateCalculator.StDevSample, 2.2803],
                 [QgsAggregateCalculator.Min, 2],
                 [QgsAggregateCalculator.Max, 8],
                 [QgsAggregateCalculator.Range, 6],
                 [QgsAggregateCalculator.Median, 3.5],
                 [QgsAggregateCalculator.CountDistinct, 5],
                 [QgsAggregateCalculator.CountMissing, 1],
                 [QgsAggregateCalculator.FirstQuartile, 2],
                 [QgsAggregateCalculator.ThirdQuartile, 5.0],
                 [QgsAggregateCalculator.InterQuartileRange, 3.0]
                 ]

        for t in tests:
            val, ok = layer.aggregate(t[0], 'fldint')
            self.assertTrue(ok)
            if isinstance(t[1], int):
                self.assertEqual(val, t[1])
            else:
                self.assertAlmostEqual(val, t[1], 3)

        # test with parameters
        layer = QgsVectorLayer("Point?field=fldstring:string", "layer", "memory")
        pr = layer.dataProvider()

        string_values = ['this', 'is', 'a', 'test']
        features = []
        for s in string_values:
            f = QgsFeature()
            f.setFields(layer.fields())
            f.setAttributes([s])
            features.append(f)
        assert pr.addFeatures(features)
        params = QgsAggregateCalculator.AggregateParameters()
        params.delimiter = ' '
        val, ok = layer.aggregate(QgsAggregateCalculator.StringConcatenate, 'fldstring', params)
        self.assertTrue(ok)
        self.assertEqual(val, 'this is a test')

    def onLayerTransparencyChanged(self, tr):
        self.transparencyTest = tr

    def test_setLayerTransparency(self):
        layer = createLayerWithOnePoint()

        self.transparencyTest = 0
        layer.layerTransparencyChanged.connect(self.onLayerTransparencyChanged)
        layer.setLayerTransparency(50)
        self.assertEqual(self.transparencyTest, 50)
        self.assertEqual(layer.layerTransparency(), 50)

    def onRendererChanged(self):
        self.rendererChanged = True

    def test_setRenderer(self):
        layer = createLayerWithOnePoint()

        self.rendererChanged = False
        layer.rendererChanged.connect(self.onRendererChanged)

        r = QgsSingleSymbolRenderer(QgsSymbol.defaultSymbol(QgsWkbTypes.PointGeometry))
        layer.setRenderer(r)
        self.assertTrue(self.rendererChanged)
        self.assertEqual(layer.renderer(), r)

    def testGetSetAliases(self):
        """ test getting and setting aliases """
        layer = createLayerWithOnePoint()

        self.assertFalse(layer.attributeAlias(0))
        self.assertFalse(layer.attributeAlias(1))
        self.assertFalse(layer.attributeAlias(2))

        layer.setFieldAlias(0, "test")
        self.assertEqual(layer.attributeAlias(0), "test")
        self.assertFalse(layer.attributeAlias(1))
        self.assertFalse(layer.attributeAlias(2))
        self.assertEqual(layer.fields().at(0).alias(), "test")

        layer.setFieldAlias(1, "test2")
        self.assertEqual(layer.attributeAlias(0), "test")
        self.assertEqual(layer.attributeAlias(1), "test2")
        self.assertFalse(layer.attributeAlias(2))
        self.assertEqual(layer.fields().at(0).alias(), "test")
        self.assertEqual(layer.fields().at(1).alias(), "test2")

        layer.setFieldAlias(1, None)
        self.assertEqual(layer.attributeAlias(0), "test")
        self.assertFalse(layer.attributeAlias(1))
        self.assertFalse(layer.attributeAlias(2))
        self.assertEqual(layer.fields().at(0).alias(), "test")
        self.assertFalse(layer.fields().at(1).alias())

        layer.removeFieldAlias(0)
        self.assertFalse(layer.attributeAlias(0))
        self.assertFalse(layer.attributeAlias(1))
        self.assertFalse(layer.attributeAlias(2))
        self.assertFalse(layer.fields().at(0).alias())
        self.assertFalse(layer.fields().at(1).alias())

    def testSaveRestoreAliases(self):
        """ test saving and restoring aliases from xml"""
        layer = createLayerWithOnePoint()

        # no default expressions
        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer2 = createLayerWithOnePoint()
        self.assertTrue(layer2.readXml(elem))
        self.assertFalse(layer2.attributeAlias(0))
        self.assertFalse(layer2.attributeAlias(1))

        # set some aliases
        layer.setFieldAlias(0, "test")
        layer.setFieldAlias(1, "test2")

        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer3 = createLayerWithOnePoint()
        self.assertTrue(layer3.readXml(elem))
        self.assertEqual(layer3.attributeAlias(0), "test")
        self.assertEqual(layer3.attributeAlias(1), "test2")
        self.assertEqual(layer3.fields().at(0).alias(), "test")
        self.assertEqual(layer3.fields().at(1).alias(), "test2")

    def testGetSetDefaults(self):
        """ test getting and setting default expressions """
        layer = createLayerWithOnePoint()

        self.assertFalse(layer.defaultValueExpression(0))
        self.assertFalse(layer.defaultValueExpression(1))
        self.assertFalse(layer.defaultValueExpression(2))

        layer.setDefaultValueExpression(0, "'test'")
        self.assertEqual(layer.defaultValueExpression(0), "'test'")
        self.assertFalse(layer.defaultValueExpression(1))
        self.assertFalse(layer.defaultValueExpression(2))
        self.assertEqual(layer.fields().at(0).defaultValueExpression(), "'test'")

        layer.setDefaultValueExpression(1, "2+2")
        self.assertEqual(layer.defaultValueExpression(0), "'test'")
        self.assertEqual(layer.defaultValueExpression(1), "2+2")
        self.assertFalse(layer.defaultValueExpression(2))
        self.assertEqual(layer.fields().at(0).defaultValueExpression(), "'test'")
        self.assertEqual(layer.fields().at(1).defaultValueExpression(), "2+2")

    def testSaveRestoreDefaults(self):
        """ test saving and restoring default expressions from xml"""
        layer = createLayerWithOnePoint()

        # no default expressions
        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer2 = createLayerWithOnePoint()
        self.assertTrue(layer2.readXml(elem))
        self.assertFalse(layer2.defaultValueExpression(0))
        self.assertFalse(layer2.defaultValueExpression(1))

        # set some default expressions
        layer.setDefaultValueExpression(0, "'test'")
        layer.setDefaultValueExpression(1, "2+2")

        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer3 = createLayerWithOnePoint()
        self.assertTrue(layer3.readXml(elem))
        self.assertEqual(layer3.defaultValueExpression(0), "'test'")
        self.assertEqual(layer3.defaultValueExpression(1), "2+2")
        self.assertEqual(layer3.fields().at(0).defaultValueExpression(), "'test'")
        self.assertEqual(layer3.fields().at(1).defaultValueExpression(), "2+2")

    def testEvaluatingDefaultExpressions(self):
        """ tests calculation of default values"""
        layer = createLayerWithOnePoint()
        layer.setDefaultValueExpression(0, "'test'")
        layer.setDefaultValueExpression(1, "2+2")
        self.assertEqual(layer.defaultValue(0), 'test')
        self.assertEqual(layer.defaultValue(1), 4)

        # using feature
        layer.setDefaultValueExpression(1, '$id * 2')
        feature = QgsFeature(4)
        feature.setValid(True)
        feature.setFields(layer.fields())
        # no feature:
        self.assertFalse(layer.defaultValue(1))
        # with feature:
        self.assertEqual(layer.defaultValue(0, feature), 'test')
        self.assertEqual(layer.defaultValue(1, feature), 8)

        # using feature geometry
        layer.setDefaultValueExpression(1, '$x * 2')
        feature.setGeometry(QgsGeometry(QgsPointV2(6, 7)))
        self.assertEqual(layer.defaultValue(1, feature), 12)

        # using contexts
        scope = QgsExpressionContextScope()
        scope.setVariable('var1', 16)
        context = QgsExpressionContext()
        context.appendScope(scope)
        layer.setDefaultValueExpression(1, '$id + @var1')
        self.assertEqual(layer.defaultValue(1, feature, context), 20)

        # if no scope passed, should use a default constructed one including layer variables
        QgsExpressionContextUtils.setLayerVariable(layer, 'var2', 4)
        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), 'var3', 8)
        layer.setDefaultValueExpression(1, 'to_int(@var2) + to_int(@var3) + $id')
        self.assertEqual(layer.defaultValue(1, feature), 16)

        # bad expression
        layer.setDefaultValueExpression(1, 'not a valid expression')
        self.assertFalse(layer.defaultValue(1))

    def testGetSetConstraints(self):
        """ test getting and setting field constraints """
        layer = createLayerWithOnePoint()

        self.assertFalse(layer.fieldConstraints(0))
        self.assertFalse(layer.fieldConstraints(1))
        self.assertFalse(layer.fieldConstraints(2))

        layer.setFieldConstraint(0, QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer.fieldConstraints(0), QgsFieldConstraints.ConstraintNotNull)
        self.assertFalse(layer.fieldConstraints(1))
        self.assertFalse(layer.fieldConstraints(2))
        self.assertEqual(layer.fields().at(0).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer.fields().at(0).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(0).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthHard)

        layer.setFieldConstraint(1, QgsFieldConstraints.ConstraintNotNull)
        layer.setFieldConstraint(1, QgsFieldConstraints.ConstraintUnique)
        self.assertEqual(layer.fieldConstraints(0), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer.fieldConstraints(1), QgsFieldConstraints.ConstraintNotNull | QgsFieldConstraints.ConstraintUnique)
        self.assertFalse(layer.fieldConstraints(2))
        self.assertEqual(layer.fields().at(0).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer.fields().at(0).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(0).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthHard)
        self.assertEqual(layer.fields().at(1).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull | QgsFieldConstraints.ConstraintUnique)
        self.assertEqual(layer.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintUnique),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(1).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthHard)
        self.assertEqual(layer.fields().at(1).constraints().constraintStrength(QgsFieldConstraints.ConstraintUnique),
                         QgsFieldConstraints.ConstraintStrengthHard)

        layer.removeFieldConstraint(1, QgsFieldConstraints.ConstraintNotNull)
        layer.removeFieldConstraint(1, QgsFieldConstraints.ConstraintUnique)
        self.assertEqual(layer.fieldConstraints(0), QgsFieldConstraints.ConstraintNotNull)
        self.assertFalse(layer.fieldConstraints(1))
        self.assertFalse(layer.fieldConstraints(2))
        self.assertEqual(layer.fields().at(0).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer.fields().at(0).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(0).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthHard)
        self.assertFalse(layer.fields().at(1).constraints().constraints())
        self.assertEqual(layer.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginNotSet)
        self.assertEqual(layer.fields().at(1).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthNotSet)

    def testSaveRestoreConstraints(self):
        """ test saving and restoring constraints from xml"""
        layer = createLayerWithOnePoint()

        # no constraints
        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer2 = createLayerWithOnePoint()
        self.assertTrue(layer2.readXml(elem))
        self.assertFalse(layer2.fieldConstraints(0))
        self.assertFalse(layer2.fieldConstraints(1))

        # set some constraints
        layer.setFieldConstraint(0, QgsFieldConstraints.ConstraintNotNull)
        layer.setFieldConstraint(1, QgsFieldConstraints.ConstraintNotNull, QgsFieldConstraints.ConstraintStrengthSoft)
        layer.setFieldConstraint(1, QgsFieldConstraints.ConstraintUnique)

        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer3 = createLayerWithOnePoint()
        self.assertTrue(layer3.readXml(elem))
        self.assertEqual(layer3.fieldConstraints(0), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer3.fieldConstraints(1), QgsFieldConstraints.ConstraintNotNull | QgsFieldConstraints.ConstraintUnique)
        self.assertEqual(layer3.fields().at(0).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull)
        self.assertEqual(layer3.fields().at(0).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(0).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthHard)
        self.assertEqual(layer3.fields().at(1).constraints().constraints(), QgsFieldConstraints.ConstraintNotNull | QgsFieldConstraints.ConstraintUnique)
        self.assertEqual(layer3.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer3.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintUnique),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer.fields().at(1).constraints().constraintStrength(QgsFieldConstraints.ConstraintNotNull),
                         QgsFieldConstraints.ConstraintStrengthSoft)
        self.assertEqual(layer.fields().at(1).constraints().constraintStrength(QgsFieldConstraints.ConstraintUnique),
                         QgsFieldConstraints.ConstraintStrengthHard)

    def testGetSetConstraintExpressions(self):
        """ test getting and setting field constraint expressions """
        layer = createLayerWithOnePoint()

        self.assertFalse(layer.constraintExpression(0))
        self.assertFalse(layer.constraintExpression(1))
        self.assertFalse(layer.constraintExpression(2))

        layer.setConstraintExpression(0, '1+2')
        self.assertEqual(layer.constraintExpression(0), '1+2')
        self.assertFalse(layer.constraintExpression(1))
        self.assertFalse(layer.constraintExpression(2))
        self.assertEqual(layer.fields().at(0).constraints().constraintExpression(), '1+2')

        layer.setConstraintExpression(1, '3+4', 'desc')
        self.assertEqual(layer.constraintExpression(0), '1+2')
        self.assertEqual(layer.constraintExpression(1), '3+4')
        self.assertEqual(layer.constraintDescription(1), 'desc')
        self.assertFalse(layer.constraintExpression(2))
        self.assertEqual(layer.fields().at(0).constraints().constraintExpression(), '1+2')
        self.assertEqual(layer.fields().at(1).constraints().constraintExpression(), '3+4')
        self.assertEqual(layer.fields().at(1).constraints().constraintDescription(), 'desc')

        layer.setConstraintExpression(1, None)
        self.assertEqual(layer.constraintExpression(0), '1+2')
        self.assertFalse(layer.constraintExpression(1))
        self.assertFalse(layer.constraintExpression(2))
        self.assertEqual(layer.fields().at(0).constraints().constraintExpression(), '1+2')
        self.assertFalse(layer.fields().at(1).constraints().constraintExpression())

    def testSaveRestoreConstraintExpressions(self):
        """ test saving and restoring constraint expressions from xml"""
        layer = createLayerWithOnePoint()

        # no constraints
        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer2 = createLayerWithOnePoint()
        self.assertTrue(layer2.readXml(elem))
        self.assertFalse(layer2.constraintExpression(0))
        self.assertFalse(layer2.constraintExpression(1))

        # set some constraints
        layer.setConstraintExpression(0, '1+2')
        layer.setConstraintExpression(1, '3+4', 'desc')

        doc = QDomDocument("testdoc")
        elem = doc.createElement("maplayer")
        self.assertTrue(layer.writeXml(elem, doc))

        layer3 = createLayerWithOnePoint()
        self.assertTrue(layer3.readXml(elem))
        self.assertEqual(layer3.constraintExpression(0), '1+2')
        self.assertEqual(layer3.constraintExpression(1), '3+4')
        self.assertEqual(layer3.constraintDescription(1), 'desc')
        self.assertEqual(layer3.fields().at(0).constraints().constraintExpression(), '1+2')
        self.assertEqual(layer3.fields().at(1).constraints().constraintExpression(), '3+4')
        self.assertEqual(layer3.fields().at(1).constraints().constraintDescription(), 'desc')
        self.assertEqual(layer3.fields().at(0).constraints().constraints(), QgsFieldConstraints.ConstraintExpression)
        self.assertEqual(layer3.fields().at(1).constraints().constraints(), QgsFieldConstraints.ConstraintExpression)
        self.assertEqual(layer3.fields().at(0).constraints().constraintOrigin(QgsFieldConstraints.ConstraintExpression),
                         QgsFieldConstraints.ConstraintOriginLayer)
        self.assertEqual(layer3.fields().at(1).constraints().constraintOrigin(QgsFieldConstraints.ConstraintExpression),
                         QgsFieldConstraints.ConstraintOriginLayer)

    def testGetFeatureLimitWithEdits(self):
        """ test getting features with a limit, when edits are present """
        layer = createLayerWithOnePoint()
        # now has one feature with id 0

        pr = layer.dataProvider()

        f1 = QgsFeature(1)
        f1.setAttributes(["test", 3])
        f1.setGeometry(QgsGeometry.fromPoint(QgsPoint(300, 200)))
        f2 = QgsFeature(2)
        f2.setAttributes(["test", 3])
        f2.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
        f3 = QgsFeature(3)
        f3.setAttributes(["test", 3])
        f3.setGeometry(QgsGeometry.fromPoint(QgsPoint(100, 200)))
        self.assertTrue(pr.addFeatures([f1, f2, f3]))

        req = QgsFeatureRequest().setLimit(2)
        self.assertEqual(len(list(layer.getFeatures(req))), 2)

        # now delete feature f1
        layer.startEditing()
        self.assertTrue(layer.deleteFeature(1))
        req = QgsFeatureRequest().setLimit(2)
        self.assertEqual(len(list(layer.getFeatures(req))), 2)
        layer.rollBack()

        # change an attribute value required by filter
        layer.startEditing()
        req = QgsFeatureRequest().setFilterExpression('fldint=3').setLimit(2)
        self.assertTrue(layer.changeAttributeValue(2, 1, 4))
        self.assertEqual(len(list(layer.getFeatures(req))), 2)
        layer.rollBack()

        layer.startEditing()
        req = QgsFeatureRequest().setFilterRect(QgsRectangle(50, 100, 150, 300)).setLimit(2)
        self.assertTrue(layer.changeGeometry(2, QgsGeometry.fromPoint(QgsPoint(500, 600))))
        self.assertEqual(len(list(layer.getFeatures(req))), 2)
        layer.rollBack()


# TODO:
# - fetch rect: feat with changed geometry: 1. in rect, 2. out of rect
# - more join tests
# - import

if __name__ == '__main__':
    unittest.main()
