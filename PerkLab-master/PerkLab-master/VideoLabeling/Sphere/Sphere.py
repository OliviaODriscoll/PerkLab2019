import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy
import math

#
# Sphere
#

class Sphere(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Sphere" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# SphereWidget
#

class SphereWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    fidList = slicer.util.getNode('line')
    numFids = fidList.GetNumberOfFiducials()
    for i in range(numFids):
      ras = [0,0,0]
      fidList.GetNthFiducialPosition(i,ras)
   # the world position is the RAS position with any transform matrices applied
      world = [0,0,0,0]
      fidList.GetNthFiducialWorldCoordinates(0,world)
   #  print(i,": RAS =",ras,", world =",world)

    #self.line = slicer.vtkMRMLMarkupsFiducialNode()
    #numFiducials = slicer.vtkMRMLMarkupsFiducialNode.GetNumberOfFiducials()

    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # Sphere button
    AddSphereButton = qt.QPushButton("Add Sphere")
    AddSphereButton.toolTip = "Add a Sphere to the scene."
    parametersFormLayout.addWidget(AddSphereButton)
    AddSphereButton.connect('clicked(bool)', self.onAddSphereButtonClicked)


    # Add vertical spacer
    self.layout.addStretch(1)

    
    #Set local var as instance attribute
    self.AddSphereButton = AddSphereButton


  def onAddSphereButtonClicked(self):
    bounds = [0]*6
    fidList = slicer.util.getNode('line')
    fidList.GetBounds(bounds)
   

    # Get the bounding box of the data
    #self.line.GetBounds(bounds)
    print bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5]

    # Find the center of the sphere by averaging the min and max x, y, and z values
    sphereX = (bounds[0]+bounds[3])/2 
    sphereY = (bounds[1]+bounds[4])/2
    sphereZ = (bounds[2]+bounds[5])/2
    sphereCenter = numpy.array([sphereX, sphereY, sphereZ])
    print sphereX, sphereY, sphereZ

    # Get the sphere diameter

    sphereDiameter = max(((bounds[3]-bounds[0])), ((bounds[4]-bounds[1])), ((bounds[5]-bounds[2])))/.7/.7
    if sphereDiameter > 0:
      sphereRadius = sphereDiameter/2
    else:
      sphereRadius = 0

    # Create a model containing a sphere
    sphere = vtk.vtkSphereSource()
    sphere.SetRadius(sphereRadius)
    sphere.SetCenter(sphereX, sphereY, sphereZ)
    #sphere.Set
    sphere.Update()
    modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
    modelNode.SetAndObservePolyData(sphere.GetOutput())
    modelNode.CreateDefaultDisplayNodes()
    #a = arrayFromModelPoints(modelNode)
    # change Y scaling
    #a[:,2] = a[:,2] * 2.5
    #arrayFromModelPointsModified(modelNode)
    

  def cleanup(self):
    pass

#
# SphereLogic
#

class SphereLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('SphereTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class SphereTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Sphere1()

  def test_Sphere1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = SphereLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
