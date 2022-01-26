from datetime import datetime

import jpype
import base64
from io import BytesIO

from PIL import Image

from . import Assist

is_array = lambda var: isinstance(var, (list, tuple))
import os
import logging
from enum import Enum


class BarCodeReader(Assist.BaseJavaClass):
      """!
       BarCodeReader encapsulates an image which may contain one or several barcodes, it then can perform ReadBarCodes operation to detect barcodes.

       This sample shows how to detect Code39 and Code128 barcodes.
       \code
       reader = BarCodeReader("test.png", None,  [DecodeType.CODE_39_STANDARD, DecodeType.CODE_128])
       for result in reader.readBarCodes():
             print("BarCode Type: " + result.getCodeTypeName())
             print("BarCode CodeText: " + result.getCodeText())
       \endcode
      """

      javaClassName = "com.aspose.mw.barcode.recognition.MwBarCodeReader"

      def __init__(self, image, rectangles, decodeTypes):
            """!
          Initializes a new instance of the BarCodeReader
          :param: image encoded as base64 string or path to image
          :param: rectangles array of object by type Rectangle
          :param: decodeTypes the array of objects by DecodeType
            """
            self.qualitySettings = None
            self.recognizedResults = None
            self.barcodeSettings = None
            image = BarCodeReader.convertToBase64Image(image)
            if not (rectangles is None):
                  if not (is_array(rectangles)):
                        rectangles = [rectangles.toString()]
                  else:
                        i = 0
                        while (i < len(rectangles)):
                              rectangles[i] = rectangles[i].toString()
                              i = i + 1
            if (decodeTypes != None):
                  if not (is_array(decodeTypes)):
                        decodeTypes = [decodeTypes]
                  i = 0
                  while (i < len(decodeTypes)):
                        decodeTypes[i] = str(decodeTypes[i].value)
                        i += 1
            try:
                  java_link = jpype.JClass(BarCodeReader.javaClassName)
                  if image == None and rectangles == None and image == None:
                        javaClass = java_link()
                  else:
                        javaClass = java_link(image, rectangles, decodeTypes)
                  super().__init__(javaClass)
                  self.init()
            except Exception as ex:
                  logging.error("Invalid arguments")
                  raise

      @staticmethod
      def construct(javaClass):
            barcodeReader = BarCodeReader(None, None, None)
            barcodeReader.setJavaClass(javaClass)
            return barcodeReader

      @staticmethod
      def convertToBase64Image(image):
            if image is None:
                  return None
            if isinstance(image, str) and os.path.exists(image):
                  image = Image.open(image)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue())

      def containsAny(self, decodeTypes):
            """!
            Determines whether any of the given decode types is included into
            :param: ...decodeTypes Types to verify.
            :return: bool Value is a true if any types are included into.
            """
            i = 0
            while (i < len(decodeTypes)):
                  decodeTypes[i] = str(decodeTypes[i].value)
                  i += 1
            return self.getJavaClass().containsAny(decodeTypes)

      def init(self):
            self.qualitySettings = QualitySettings(self.getJavaClass().getQualitySettings())
            self.barcodeSettings = BarcodeSettings.construct(self.getJavaClass().getBarcodeSettings())

      def getTimeout(self):
            """!
            Gets the timeout of recognition process in milliseconds.
            \code
               reader = BarCodeReader("test.png", None, None)
               reader.setTimeout(5000)
               for result in reader.readBarCodes():
                  print("BarCode CodeText: " + result.getCodeText())
            \endcode
         :return: The timeout.
            """
            return self.getJavaClass().getTimeout()

      def setTimeout(self, value):
            """!
             Sets the timeout of recognition process in milliseconds.
             \code
                   reader = BarCodeReader("test.png", None, None)
                   reader.setTimeout(5000)
                   for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
             \endcode
          :param: value The timeout.
            """
            self.getJavaClass().setTimeout(value)

      def getChecksumValidation(self):
            """!
          Enable checksum validation during recognition for 1D barcodes.

          Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.

          Checksum never used: Codabar

          Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN

          Checksum always used: Rest symbologies

          This sample shows influence of ChecksumValidation on recognition quality and results
          \code
                generator = BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
                generator.save("test.png")
                reader = BarCodeReader("test.png", None,  DecodeType.EAN_13)
                #checksum disabled
                reader.setChecksumValidation(ChecksumValidation.OFF)
                for result in reader.readBarCodes():
                    print("BarCode CodeText: " + result.getCodeText())
                    print("BarCode Value: " + result.getExtended().getOneD().getValue())
                    print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
                reader = BarCodeReader("test.png", None,  DecodeType.EAN_13)
                #checksum enabled
                reader.setChecksumValidation(ChecksumValidation.ON)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
                   print("BarCode Value: " + result.getExtended().getOneD().getValue())
                   print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
          \endcode
          The checksum validation flag.
            """
            return ChecksumValidation(int(self.getJavaClass().getChecksumValidation()))

      def setChecksumValidation(self, value):
            """!
          Enable checksum validation during recognition for 1D barcodes.

          Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.

          Checksum never used: Codabar

          Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN

          Checksum always used: Rest symbologies

          This sample shows influence of ChecksumValidation on recognition quality and results
          \code
                generator = BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
                generator.save("test.png")
                reader = BarCodeReader("test.png", None,  DecodeType.EAN_13)
                #checksum disabled
                reader.setChecksumValidation(ChecksumValidation.OFF)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
                   print("BarCode Value: " + result.getExtended().getOneD().getValue())
                   print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
                reader = BarCodeReader("test.png", None,  DecodeType.EAN_13)
                #checksum enabled
                reader.setChecksumValidation(ChecksumValidation.ON)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
                   print("BarCode Value: " + result.getExtended().getOneD().getValue())
                   print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
         \endcode
          The checksum validation flag.
            """
            self.getJavaClass().setChecksumValidation(value.value)

      def getStripFNC(self):
            """!
          Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.

          This sample shows how to strip FNC characters
          \code
                generator = BarcodeGenerator(EncodeTypes.GS1Code128, "(02)04006664241007(37)1(400)7019590754")
                generator.save("test.png")
                reader = BarCodeReader("test.png", None,  DecodeType.CODE_128)
                #StripFNC disabled
                reader.setStripFNC(false)
                for result in reader.readBarCodes():
                    print("BarCode CodeText: " + result.getCodeText())
                reader = BarCodeReader("test.png", None,  DecodeType.CODE_128)
                #StripFNC enabled
                reader.setStripFNC(true)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
          \endcode
            """
            return self.getJavaClass().getStripFNC()

      def setStripFNC(self, value):
            """!
                Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.

                This sample shows how to strip FNC characters
                \code
                generator = BarcodeGenerator(EncodeTypes.GS1Code128, "(02)04006664241007(37)1(400)7019590754")
                generator.save("test.png")
                reader = BarCodeReader("test.png", None,  DecodeType.CODE_128)
                #StripFNC disabled
                reader.setStripFNC(false)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
                reader = BarCodeReader("test.png", None,  DecodeType.CODE_128)
                #StripFNC enabled
                reader.setStripFNC(true)
                for result in reader.readBarCodes():
                   print("BarCode CodeText: " + result.getCodeText())
               \endcode
            """
            self.getJavaClass().setStripFNC(value)

      def getCustomerInformationInterpretingType(self):
            """!
            Gets the Interpreting Type for the Customer Information of AustralianPost BarCode.Default is CustomerInformationInterpretingType.OTHER.
            """
            return CustomerInformationInterpretingType(self.getJavaClass().getCustomerInformationInterpretingType())

      def setCustomerInformationInterpretingType(self, value):
            """!
            Sets the Interpreting Type for the Customer Information of AustralianPost BarCode.Default is CustomerInformationInterpretingType.OTHER.
            """
            self.getJavaClass().setCustomerInformationInterpretingType(value.value)

      def abort(self):
            self.getJavaClass().abort()

      def getFoundBarCodes(self):
            """!
                Gets recognized BarCodeResult array

                This sample shows how to read barcodes with BarCodeReader
               \code
                reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                reader.readBarCodes()
                for(let i = 0 reader.getFoundCount() > i ++i)
                   print("BarCode CodeText: " +  reader.getFoundBarCodes()[i].getCodeText())
               \endcode
                Value: The recognized BarCodeResult array
            """
            return self.recognizedResults

      def getFoundCount(self):
            """!
            Gets recognized barcodes count<hr><blockquote>

            This sample shows how to read barcodes with BarCodeReader
            \code
                reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                reader.readBarCodes()
                for(let i = 0 reader.getFoundCount() > i ++i)
                   print("BarCode CodeText: " + reader.getFoundBarCodes()[i].getCodeText())
            \endcode
            Value: The recognized barcodes count
            """
            return self.getJavaClass().getFoundCount()

      def readBarCodes(self):
            """!
                 Reads BarCodeResult from the image.

                This sample shows how to read barcodes with BarCodeReader
                \code
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      for result in reader.readBarCodes():
                         print("BarCode CodeText: " + result.getCodeText())
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      reader.readBarCodes()
                      for(let i = 0 reader.getFoundCount() > i ++i)
                         print("BarCode CodeText: " + reader.getFoundBarCodes()[i].getCodeText())
                \endcode
                :return: Returns array of recognized {@code BarCodeResult}s on the image. If nothing is recognized, zero array is returned.
            """
            try:
                  self.recognizedResults = []
                  javaReadBarcodes = self.getJavaClass().readBarCodes()
                  i = 0
                  length = javaReadBarcodes.length
                  while (i < length):
                        self.recognizedResults.append(BarCodeResult(javaReadBarcodes[i]))
                        i += 1
                  return self.recognizedResults
            except Exception as e:
                  if "RecognitionAbortedException" in str(e):
                        raise RecognitionAbortedException(str(e), int(e.getExecutionTime()))
                  raise e

      def getQualitySettings(self):
            """!
                QualitySettings allows to configure recognition quality and speed manually.

                You can quickly set up QualitySettings by embedded presets: HighPerformance, NormalQuality,

                HighQuality, MaxBarCodes or you can manually configure separate options.

                Default value of QualitySettings is NormalQuality.

                This sample shows how to use QualitySettings with BarCodeReader
                \code
                      reader = BarCodeReader("test.png", None, None)
                       #set high performance mode
                      reader.setQualitySettings(QualitySettings.getHighPerformance())
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      #normal quality mode is set by default
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      #set high performance mode
                      reader.setQualitySettings(QualitySettings.getHighPerformance())
                      #set separate options
                      reader.getQualitySettings().setAllowMedianSmoothing(true)
                      reader.getQualitySettings().setMedianSmoothingWindowSize(5)
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                \endcode
                QualitySettings to configure recognition quality and speed.
            """
            return self.qualitySettings

      def setQualitySettings(self, value):
            """!
                QualitySettings allows to configure recognition quality and speed manually.

                 You can quickly set up QualitySettings by embedded presets: HighPerformance, NormalQuality,

                 HighQuality, MaxBarCodes or you can manually configure separate options.

                 Default value of QualitySettings is NormalQuality.

                This sample shows how to use QualitySettings with BarCodeReader
                \code
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      #set high performance mode
                      reader.setQualitySettings(QualitySettings.getHighPerformance())
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                      #normal quality mode is set by default
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                      reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                       #set high performance mode
                      reader.setQualitySettings(QualitySettings.getHighPerformance())
                      #set separate options
                      reader.getQualitySettings().setAllowMedianSmoothing(true)
                      reader.getQualitySettings().setMedianSmoothingWindowSize(5)
                      for result in reader.readBarCodes():
                        print("BarCode CodeText: " + result.getCodeText())
                \endcode
                QualitySettings to configure recognition quality and speed.
            """
            self.getJavaClass().setQualitySettings(value.getJavaClass())

      def getBarcodeSettings(self):
            """!
            The main BarCode decoding parameters. Contains parameters which make influence on recognized data.

            return The main BarCode decoding parameters
            """
            return self.barcodeSettings

      def getDetectEncoding(self):
            """!
                 A flag which force engine to detect codetext encoding for Unicode codesets.

                This sample shows how to detect text encoding on the fly if DetectEncoding is enabled
                \code
                      image = "image.png"
                      generator = BarcodeGenerator(EncodeTypes.QR, "пїЅпїЅпїЅпїЅпїЅ"))
                      generator.getParameters().getBarcode().getQR().setCodeTextEncoding("UTF-8")
                      generator.save(image, BarCodeImageFormat.getPng())
                          #detects encoding for Unicode codesets is enabled
                      reader = BarCodeReader(image, None, DecodeType.QR)
                      reader.setDetectEncoding(true)
                      for result in reader.readBarCodes():
                         print("BarCode CodeText: " + result.getCodeText())
                          #detect encoding is disabled
                      reader = BarCodeReader(image, None, DecodeType.QR)
                      reader.setDetectEncoding(false)
                      for result in reader.readBarCodes():
                         print("BarCode CodeText: " + result.getCodeText())
               \endcode
            """
            return self.getJavaClass().getDetectEncoding()

      def setDetectEncoding(self, value):
            """!
                 A flag which force engine to detect codetext encoding for Unicode codesets.

                This sample shows how to detect text encoding on the fly if DetectEncoding is enabled
                \code
                      let image = "image.png"
                      generator = BarcodeGenerator(EncodeTypes.QR, "пїЅпїЅпїЅпїЅпїЅ")
                      generator.getParameters().getBarcode().getQR().setCodeTextEncoding("UTF-8")
                      generator.save(image, BarCodeImageFormat.getPng())
                      #detects encoding for Unicode codesets is enabled
                      reader = BarCodeReader(image, None, DecodeType.QR)
                      reader.setDetectEncoding(true)
                      for result in reader.readBarCodes():
                         print("BarCode CodeText: " + result.getCodeText())
                      #detect encoding is disabled
                      reader = BarCodeReader(image, None, DecodeType.QR)
                      reader.setDetectEncoding(true)
                      for result in reader.readBarCodes():
                         print("BarCode CodeText: " + result.getCodeText())
               \endcode
            """
            self.getJavaClass().setDetectEncoding(value)

      def setBarCodeImage(self, image, areas):
            """!
          Sets bitmap image and areas for Recognition.

          Must be called before ReadBarCodes() method.

          This sample shows how to detect Code39 and Code128 barcodes.
          \code
                let bmp = "test.png"
                reader = BarCodeReader()
                reader.setBarCodeReadType([ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                var img = Image()
                img.src = 'path_to_image'
                width = img.width
                height = img.height
                reader.setBarCodeImage(bmp, [Rectangle(0, 0, width, height)])
                for result in results:
                   print("BarCode Type: " + result.getCodeTypeName())
                   print("BarCode CodeText: " + result.getCodeText())
         \endcode
          :param: value The bitmap image for Recognition.
          :param: areas areas list for recognition
          @throws BarCodeException
            """
            image = BarCodeReader.convertToBase64Image(image)
            stringAreas = []
            isAllRectanglesNotNull = False
            if (areas is not None):
                  if (isinstance(areas, list) and len(areas) > 0):
                        i = 0
                        while (i < len(areas)):
                              if ((areas[i] != None)):
                                    isAllRectanglesNotNull |= True
                                    stringAreas.append(areas[i].toString())
                              i += 1
                        if (isAllRectanglesNotNull == False):
                              stringAreas = []
            if (len(stringAreas) == 0):
                  self.getJavaClass().setBarCodeImage(image)
            else:
                  self.getJavaClass().setBarCodeImage(image, stringAreas)

      def setBarCodeReadType(self, types):
            """!
           Sets SingleDecodeType type array for Recognition.

           Must be called before readBarCodes() method.

           This sample shows how to detect Code39 and Code128 barcodes.
           \code
                reader = BarCodeReader()
                reader.setBarCodeReadType([ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
                reader.setBarCodeImage("test.png")
                for result in reader.readBarCodes():
                    print("BarCode Type: " + result.getCodeTypeName())
                    print("BarCode CodeText: " + result.getCodeText())
         \endcode
          :param: types The SingleDecodeType type array to read.
            """
            i = 0
            if (isinstance(types, list)):
                  while (i < len(types)):
                        types[i] = str(types[i].value)
                        i += 1
            else:
                  types = [str(types.value)]
            self.getJavaClass().setBarCodeReadType(types)

      def getBarCodeDecodeType(self):
            return DecodeType(int(self.getJavaClass().getBarCodeDecodeType()))

      def exportToXml(self, xmlFile):
            """!
           Exports BarCode properties to the xml-file specified
           :param: xmlFile The name of  the file
           :return: Whether or not export completed successfully.
           Returns True in case of success False Otherwise
            """
            try:
                  xmlData = str(self.getJavaClass().exportToXml())
                  isSaved = xmlData != None
                  if isSaved:
                        text_file = open(xmlFile, "w")
                        text_file.write(xmlData)
                        text_file.close()
                  return isSaved
            except Exception as ex:
                  barcode_exception = Assist.BarCodeException(str(ex))
                  raise barcode_exception

      @staticmethod
      def importFromXml(xmlFile):
            """!
            Exports BarCode properties to the xml-file specified
            :param xmlFile: xmlFile The name of  the file
            :return:Whether or not export completed successfully. Returns True in case of success; False Otherwise
            """
            try:
                  with open(xmlFile, 'r') as file:
                        xmlData = file.read()
                        java_class_link = jpype.JClass(BarCodeReader.javaClassName)
                        return BarCodeReader.construct(java_class_link.importFromXml(xmlData[3:]))
            except Exception as ex:
                  barcode_exception = Assist.BarCodeException(ex)
                  raise barcode_exception

class Quadrangle(Assist.BaseJavaClass):
      """!
    Stores a set of four Points that represent a Quadrangle region.
      """
      javaClassName = "com.aspose.mw.barcode.recognition.MwQuadrangle"

      @staticmethod
      def EMPTY():
            """!
            Represents a Quadrangle structure with its properties left uninitialized.Value: Quadrangle
            """
            return Quadrangle(Assist.Point(0, 0), Assist.Point(0, 0), Assist.Point(0, 0), Assist.Point(0, 0))

      @staticmethod
      def construct(*args):
            quadrangle = Quadrangle.EMPTY()
            quadrangle.setJavaClass(args[0])
            return quadrangle

      def __init__(self, leftTop, rightTop, rightBottom, leftBottom):
            """!
            Initializes a new instance of the Quadrangle structure with the describing points.
            :param: leftTop A Point that represents the left-top corner of the Quadrangle.
            :param: rightTop A Point that represents the right-top corner of the Quadrangle.
            :param: rightBottom A Point that represents the right-bottom corner of the Quadrangle.
            :param: leftBottom A Point that represents the left-bottom corner of the Quadrangle.
            """
            self.leftTop = leftTop
            self.rightTop = rightTop
            self.rightBottom = rightBottom
            self.leftBottom = leftBottom
            java_link = jpype.JClass(self.javaClassName)
            javaClass = java_link(leftTop.getJavaClass(), rightTop.getJavaClass(), rightBottom.getJavaClass(),
                                  leftBottom.getJavaClass())
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.leftTop = Assist.Point.construct(self.getJavaClass().getLeftTop())
            self.rightTop = Assist.Point.construct(self.getJavaClass().getRightTop())
            self.rightBottom = Assist.Point.construct(self.getJavaClass().getRightBottom())
            self.leftBottom = Assist.Point.construct(self.getJavaClass().getLeftBottom())

      def getLeftTop(self):
            """!
            Gets left-top corner Point of Quadrangle regionValue: A left-top corner Point of Quadrangle region
            """
            return self.leftTop

      def setLeftTop(self, value):
            """!
           Gets left-top corner Point of Quadrangle regionValue: A left-top corner Point of Quadrangle region
            """
            self.leftTop = value
            self.getJavaClass().setLeftTop(value.getJavaClass())

      def getRightTop(self):
            """!
           Gets right-top corner Point of Quadrangle regionValue: A right-top corner Point of Quadrangle region
            """
            return self.rightTop

      def setRightTop(self, value):
            """!
            Gets right-top corner Point of Quadrangle regionValue: A right-top corner Point of Quadrangle region
            """
            self.rightTop = value
            self.getJavaClass().setRightTop(value.getJavaClass())

      def getRightBottom(self):
            """!
            Gets right-bottom corner Point of Quadrangle regionValue: A right-bottom corner Point of Quadrangle region
            """
            return self.rightBottom

      def setRightBottom(self, value):
            """!
           Gets right-bottom corner Point of Quadrangle regionValue: A right-bottom corner Point of Quadrangle region
            """
            self.rightBottom = value
            self.getJavaClass().setRightBottom(value.getJavaClass())

      def getLeftBottom(self):
            """!
           Gets left-bottom corner Point of Quadrangle regionValue: A left-bottom corner Point of Quadrangle region
            """
            return self.leftBottom

      def setLeftBottom(self, value):
            """!
           Gets left-bottom corner Point of Quadrangle regionValue: A left-bottom corner Point of Quadrangle region
            """
            self.leftBottom = value
            self.getJavaClass().setLeftBottom(value.getJavaClass())

      def isEmpty(self):
            """!
            Tests whether all Points of this Quadrangle have values of zero.Value: Returns true if all Points of this Quadrangle have values of zero otherwise, false.
            """
            return self.getJavaClass().isEmpty()

      def contains(self, pt):
            """!
           Determines if the specified Point is contained within this Quadrangle structure.
           :param: pt The Point to test.
           :return: Returns true if Point is contained within this Quadrangle structure otherwise, false.
            """
            return self.getJavaClass().contains(pt.getJavaClass())

      def containsPoint(self, x, y):
            """!
           Determines if the specified point is contained within this Quadrangle structure.
           :param: x The x point cordinate.
           :param: y The y point cordinate.
           :return: Returns true if point is contained within this Quadrangle structure otherwise, false.
            """
            return self.getJavaClass().contains(x, y)

      def containsQuadrangle(self, quad):
            """!
           Determines if the specified Quadrangle is contained or intersect this Quadrangle structure.
           :param: quad The Quadrangle to test.
           :return: Returns true if Quadrangle is contained or intersect this Quadrangle structure otherwise, false.
            """
            return self.getJavaClass().contains(quad.getJavaClass())

      def containsRectangle(self, rect):
            """!
           Determines if the specified Rectangle is contained or intersect this Quadrangle structure.
           :param: rect The Rectangle to test.
           :return: Returns true if Rectangle is contained or intersect this Quadrangle structure otherwise, false.
            """
            return self.getJavaClass().contains(rect)

      def equals(self, other):
            """!
            Returns a value indicating whether this instance is equal to a specified Quadrangle value.
            :param: other An Quadrangle value to compare to this instance.
            :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(other.getJavaClass())

      def hashCode(self):
            """!
            Returns the hash code for this instance.
            :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
            Returns a human-readable string representation of this Quadrangle.
            :return: A string that represents this Quadrangle.
            """
            return self.getJavaClass().toString()

      def getBoundingRectangle(self):
            """!
            Creates Rectangle bounding this Quadrangle
            :return: returns Rectangle bounding this Quadrangle
            """
            return Assist.Rectangle.construct(self.getJavaClass().getBoundingRectangle())


class QRExtendedParameters(Assist.BaseJavaClass):
      """!
     Stores a QR Structured Append information of recognized barcode

     This sample shows how to get QR Structured Append data
     \code
            reader = BarCodeReader("test.png", None,  DecodeType.QR)
            for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeTypeName())
              print("BarCode CodeText: " + result.getCodeText())
              print("QR Structured Append Quantity: " + result.getExtended().getQR().getQRStructuredAppendModeBarCodesQuantity())
              print("QR Structured Append Index: " + result.getExtended().getQR().getQRStructuredAppendModeBarCodeIndex())
              print("QR Structured Append ParityData: " + result.getExtended().getQR().getQRStructuredAppendModeParityData())
     \endcode
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            return
            # TODO: Implement init() method.

      def getQRStructuredAppendModeBarCodesQuantity(self):
            """!
            Gets the QR structured append mode barcodes quantity. Default value is -1.Value: The quantity of the QR structured append mode barcode.
            """
            return self.getJavaClass().getQRStructuredAppendModeBarCodesQuantity()

      def getQRStructuredAppendModeBarCodeIndex(self):
            """!
           Gets the index of the QR structured append mode barcode. Index starts from 0. Default value is -1.Value: The quantity of the QR structured append mode barcode.
            """
            return self.getJavaClass().getQRStructuredAppendModeBarCodeIndex()

      def getQRStructuredAppendModeParityData(self):
            """!
           Gets the QR structured append mode parity data. Default value is -1.Value: The index of the QR structured append mode barcode.
            """
            return self.getJavaClass().getQRStructuredAppendModeParityData()

      def isEmpty(self):
            return self.getJavaClass().isEmpty()

      def equals(self, obj):
            """!
           Returns a value indicating whether this instance is equal to a specified QRExtendedParameters value.
           :param: obj An object value to compare to this instance.
           :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
           Returns the hash code for this instance.
          :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this QRExtendedParameters.
           :return: A string that represents this QRExtendedParameters.
            """
            return self.getJavaClass().toString()


class Pdf417ExtendedParameters(Assist.BaseJavaClass):
      """!
      Stores a MacroPdf417 metadata information of recognized barcode

     This sample shows how to get Macro Pdf417 metadata
     \code
          generator = BarcodeGenerator(EncodeTypes.MacroPdf417, "12345")
          generator.getParameters().getBarcode().getPdf417().setPdf417MacroFileID(10)
          generator.getParameters().getBarcode().getPdf417().setPdf417MacroSegmentsCount(2)
          generator.getParameters().getBarcode().getPdf417().setPdf417MacroSegmentID(1)
          generator.save("test.png")
          reader = BarCodeReader("test.png", None,  DecodeType.MACRO_PDF_417)
          for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeTypeName())
              print("BarCode CodeText: " + result.getCodeText())
              print("Macro Pdf417 FileID: " + result.getExtended().getPdf417().getMacroPdf417FileID())
              print("Macro Pdf417 Segments: " + result.getExtended().getPdf417().getMacroPdf417SegmentsCount())
              print("Macro Pdf417 SegmentID: " + result.getExtended().getPdf417().getMacroPdf417SegmentID())
     \endcode
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            return
            # TODO: Implement init() method.

      def getMacroPdf417FileID(self):
            """!
           Gets the file ID of the barcode, only available with MacroPdf417.Value: The file ID for MacroPdf417
            """
            return str(self.getJavaClass().getMacroPdf417FileID())

      def getMacroPdf417SegmentID(self):
            """!
            Gets the segment ID of the barcode,only available with MacroPdf417.Value: The segment ID of the barcode.
            """
            return int(self.getJavaClass().getMacroPdf417SegmentID())

      def getMacroPdf417SegmentsCount(self):
            """!
           Gets macro pdf417 barcode segments count. Default value is -1.Value: Segments count.
            """
            return int(self.getJavaClass().getMacroPdf417SegmentsCount())

      def getMacroPdf417FileName(self):
            """!
           Macro PDF417 file name (optional).
          :return: File name.
            """
            return self.getJavaClass().getMacroPdf417FileName()

      def getMacroPdf417FileSize(self):
            """!
           Macro PDF417 file size (optional).
           :return: File size.
            """
            return self.getJavaClass().getMacroPdf417FileSize()

      def getMacroPdf417Sender(self):
            """!
           Macro PDF417 sender name (optional).
           :return: Sender name
            """
            return self.getJavaClass().getMacroPdf417Sender()

      def getMacroPdf417Addressee(self):
            """!
           Macro PDF417 addressee name (optional).
           :return: Addressee name.
            """
            return self.getJavaClass().getMacroPdf417Addressee()

      def getMacroPdf417TimeStamp(self):
            """!
            Macro PDF417 time stamp (optional).
            :return: Time stamp.
            """
            return datetime.fromtimestamp(int(str(self.getJavaClass().getMacroPdf417TimeStamp())))

      def getMacroPdf417Checksum(self):
            """!
           Macro PDF417 checksum (optional).
           :return: Checksum.
            """
            return self.getJavaClass().getMacroPdf417Checksum()

      def isEmpty(self):
            """!
           Tests whether all parameters has only default values
           Value: Returns {@code <b>true</b>} if all parameters has only default values otherwise, {@code <b>false</b>}.
            """
            return self.getJavaClass().isEmpty()

      def equals(self, obj):
            """!
           Returns a value indicating whether this instance is equal to a specified Pdf417ExtendedParameters value.
           :param: obj An System.Object value to compare to this instance.
           :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
            Returns the hash code for this instance.
            :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this Pdf417ExtendedParameters.
           :return: A string that represents this Pdf417ExtendedParameters.
            """
            return self.getJavaClass().toString()


class OneDExtendedParameters(Assist.BaseJavaClass):
      """!
     Stores special data of 1D recognized barcode like separate codetext and checksum

    This sample shows how to get 1D barcode value and checksum
    \code
          generator = BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
          generator.save("test.png")
          reader = BarCodeReader("test.png", None,  DecodeType.EAN_13)
          for result in reader.readBarCodes():
           print("BarCode Type: " + result.getCodeTypeName())
           print("BarCode CodeText: " + result.getCodeText())
           print("BarCode Value: " + result.getExtended().getOneD().getValue())
           print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
      \endcode
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            return
            # TODO: Implement init() method.

      def getValue(self):
            """!
           Gets the codetext of 1D barcodes without checksum. Value: The codetext of 1D barcodes without checksum.
            """
            return self.getJavaClass().getValue()

      def getCheckSum(self):
            """!
           Gets the checksum for 1D barcodes. Value: The checksum for 1D barcode.
            """
            return self.getJavaClass().getCheckSum()

      def isEmpty(self):
            """!
            Tests whether all parameters has only default values
            Value: Returns {@code <b>true</b>} if all parameters has only default values otherwise, {@code <b>false</b>}.
            """
            return self.getJavaClass().isEmpty()

      def equals(self, obj):
            """!
           Returns a value indicating whether this instance is equal to a specified OneDExtendedParameters value.
           :param: obj An System.Object value to compare to this instance.
           :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
            Returns the hash code for this instance.
           :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this OneDExtendedParameters.
           :return: A string that represents this OneDExtendedParameters.
            """
            return self.getJavaClass().toString()


class Code128ExtendedParameters(Assist.BaseJavaClass):
      """!
      Stores special data of Code128 recognized barcode

      Represents the recognized barcode's region and barcode angle

     This sample shows how to get code128 raw values
     \code
           generator = BarcodeGenerator(EncodeTypes.Code128, "12345")
           generator.save("test.png")
           reader = BarCodeReader("test.png", None,  DecodeType.CODE_128)
           for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeTypeName())
              print("BarCode CodeText: " + result.getCodeText())
              print("Code128 Data Portions: " + result.getExtended().getCode128())
      \endcode
      """

      def __init__(self, javaClass):
            self.code128DataPortions = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.code128DataPortions = Code128ExtendedParameters.convertCode128DataPortions(
                  self.getJavaClass().getCode128DataPortions())

      def convertCode128DataPortions(javaCode128DataPortions):
            code128DataPortionsValues = javaCode128DataPortions
            code128DataPortions = []
            i = 0
            while (i < len(code128DataPortionsValues)):
                  code128DataPortions.append(Code128DataPortion.construct(code128DataPortionsValues[i]))
                  i += 1
            return code128DataPortions

      def getCode128DataPortions(self):
            """!
           Gets Code128DataPortion array of recognized Code128 barcode Value of the Code128DataPortion.
            """
            return self.code128DataPortions

      def isEmpty(self):
            return self.getJavaClass().isEmpty()

      def equals(self, obj):
            """!
          Returns a value indicating whether this instance is equal to a specified Code128ExtendedParameters value.
          :param: obj An System.Object value to compare to this instance.
          :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
          Returns the hash code for this instance.
          :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this Code128ExtendedParameters.
          :return: A string that represents this Code128ExtendedParameters.
            """
            return self.getJavaClass().toString()


class BarcodeSvmDetectorSettings(Assist.BaseJavaClass):
      """!
     Barcode detector settings.
      """
      javaClassName = "com.aspose.mw.barcode.recognition.MwBarcodeSvmDetectorSettings"

      HighPerformance = 0
      """!
      High performance detection preset.
        Default for {@code QualitySettings.PresetType.HighPerformance}
      """

      NormalQuality = 1
      """!
       Normal quality detection preset.
      Default for {@code QualitySettings.PresetType.NormalQuality}
      """

      HighQuality = 2
      """!
      High quality detection preset.
     Default for {@code QualitySettings.PresetType.HighQualityDetection} and {@code QualitySettings.PresetType.HighQuality}
      """

      MaxQuality = 3
      """!
      Max quality detection preset.
      Default for {@code QualitySettings.PresetType.MaxQualityDetection} and {@code QualitySettings.PresetType.MaxBarCodes}
      """

      def __init__(self, javaClass):
            self.scanWindowSizes = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.scanWindowSizes = BarcodeSvmDetectorSettings.convertScanWindowSizes(
                  self.getJavaClass().getScanWindowSizes())
            # TODO: Implement init() method.

      def convertScanWindowSizes(javaScanWindowSizes):
            scanWindowSizes = []
            i = 0
            while (i < javaScanWindowSizes.size()):
                  scanWindowSizes.append(str(javaScanWindowSizes.get(i)))
                  i += 1
            return scanWindowSizes

      def getScanWindowSizes(self):
            """!
           Scan window sizes in pixels.
           Allowed sizes are 10, 15, 20, 25, 30.
           Scanning with small window size takes more time and provides more accuracy but may fail in detecting very big barcodes.
           Combining of several window sizes can improve detection quality.
            """
            return self.scanWindowSizes

      def setScanWindowSizes(self, value):
            """!
           Scan window sizes in pixels.
            Allowed sizes are 10, 15, 20, 25, 30.
           Scanning with small window size takes more time and provides more accuracy but may fail in detecting very big barcodes.
           Combining of several window sizes can improve detection quality.
            """
            self.scanWindowSizes = value

            ArrayList = jpype.JClass('java.util.ArrayList')
            valueList = ArrayList()
            for item in value:
                  valueList.add(item)
            self.getJavaClass().setScanWindowSizes(valueList)

      def getSimilarityCoef(self):
            """!
           Similarity coefficient depends on how homogeneous barcodes are.
           Use high value for for clear barcodes.
           Use low values to detect barcodes that ara partly damaged or not lighten evenly.
           Similarity coefficient must be between [0.5, 0.9]
            """
            return self.getJavaClass().getSimilarityCoef()

      def setSimilarityCoef(self, value):
            """!
            Similarity coefficient depends on how homogeneous barcodes are.
           Use high value for for clear barcodes.
           Use low values to detect barcodes that ara partly damaged or not lighten evenly.
           Similarity coefficient must be between [0.5, 0.9]
            """
            self.getJavaClass().setSimilarityCoef(value)

      def getRegionLikelihoodThresholdPercent(self):
            """!
           Sets threshold for detected regions that may contain barcodes.
           Value 0.7 means that bottom 70% of possible regions are filtered out and not processed further.
           Region likelihood threshold must be between [0.05, 0.9]
           Use high values for clear images with few barcodes.
           Use low values for images with many barcodes or for noisy images.
           Low value may lead to a bigger recognition time.
            """
            return self.getJavaClass().getRegionLikelihoodThresholdPercent()

      def setRegionLikelihoodThresholdPercent(self, value):
            """!
            Sets threshold for detected regions that may contain barcodes.
            Value 0.7 means that bottom 70% of possible regions are filtered out and not processed further.
            Region likelihood threshold must be between [0.05, 0.9]
            Use high values for clear images with few barcodes.
            Use low values for images with many barcodes or for noisy images.
            Low value may lead to a bigger recognition time.
            """
            self.getJavaClass().setRegionLikelihoodThresholdPercent(value)

      def getSkipDiagonalSearch(self):
            """!
            Allows detector to skip search for diagonal barcodes.
            Setting it to false will increase detection time but allow to find diagonal barcodes that can be missed otherwise.
            Enabling of diagonal search leads to a bigger detection time.
            """
            return self.getJavaClass().getSkipDiagonalSearch()

      def setSkipDiagonalSearch(self, value):
            """!
            Allows detector to skip search for diagonal barcodes.
            Setting it to false will increase detection time but allow to find diagonal barcodes that can be missed otherwise.
            Enabling of diagonal search leads to a bigger detection time.
            """
            self.getJavaClass().setSkipDiagonalSearch(value)

      def getMedianFilterWindowSize(self):
            """!
            Window size for median smoothing.
            Typical values are 3 or 4. 0 means no median smoothing.
            Default value is 0.
            Median filter window size must be between [0, 10]
            """
            return self.getJavaClass().getMedianFilterWindowSize()

      def setMedianFilterWindowSize(self, value):
            """!
           Window size for median smoothing.
           Typical values are 3 or 4. 0 means no median smoothing.
           Default value is 0.
           Median filter window size must be between [0, 10]
            """
            self.getJavaClass().setMedianFilterWindowSize(value)

      @staticmethod
      def getHighPerformance():
            """!
           High performance detection preset.
           Default for QualitySettings.PresetType.HighPerformance
            """
            return BarcodeSvmDetectorSettings(BarcodeSvmDetectorSettings.HighPerformance)

      @staticmethod
      def getNormalQuality():
            """!
          Normal quality detection preset.
          Default for QualitySettings.PresetType.NormalQuality
            """
            return BarcodeSvmDetectorSettings(BarcodeSvmDetectorSettings.NormalQuality)

      @staticmethod
      def getHighQuality():
            """!
           High quality detection preset.
           Default for QualitySettings.PresetType.HighQualityDetection and QualitySettings.PresetType.HighQuality
            """
            return BarcodeSvmDetectorSettings(BarcodeSvmDetectorSettings.HighQuality)

      @staticmethod
      def getMaxQuality():
            """!
           Max quality detection preset.
           Default for QualitySettings.PresetType.MaxQualityDetection and QualitySettings.PresetType.MaxBarCodes
            """
            return BarcodeSvmDetectorSettings(BarcodeSvmDetectorSettings.MaxQuality)


class BarCodeResult(Assist.BaseJavaClass):
      """!
      Stores recognized barcode data like SingleDecodeType type, {@code string} codetext,
     BarCodeRegionParameters region and other parameters
    This sample shows how to obtain BarCodeResult.
    \code
          generator = BarcodeGenerator(EncodeTypes.Code128, "12345")
          generator.save("test.png")
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeTypeName())
              print("BarCode CodeText: " + result.getCodeText())
              print("BarCode Confidence: " + result.getConfidence())
              print("BarCode ReadingQuality: " + result.getReadingQuality())
              print("BarCode Angle: " + result.getRegion().getAngle())
    \endcode
      """

      def __init__(self, javaClass):
            self.region = None
            self.extended = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.region = BarCodeRegionParameters(self.getJavaClass().getRegion())
            self.extended = BarCodeExtendedParameters(self.getJavaClass().getExtended())

      def getReadingQuality(self):
            """!
           Gets the reading quality. Works for 1D and postal barcodes. Value: The reading quality percent
            """
            return self.getJavaClass().getReadingQuality()

      def getConfidence(self):
            """!
           Gets recognition confidence level of the recognized barcode Value: BarCodeConfidence.

           Strong does not have fakes or misrecognitions, BarCodeConfidence.Moderate
           could sometimes have fakes or incorrect codetext because this confidence<br> level for barcodews with weak cheksum or even without it,

           BarCodeConfidence.NONE always has incorrect codetext and could be fake recognitions
            """
            return BarCodeConfidence(str(self.getJavaClass().getConfidence()))

      def getCodeText(self):
            """!
            Gets the code text Value: The code text of the barcode
            """
            return str(self.getJavaClass().getCodeText())

      def getCodeBytes(self):
            """!
            Gets the encoded code bytes Value: The code bytes of the barcode
            """
            _str = str(self.getJavaClass().getCodeBytes())
            return _str.split(",")

      def getCodeType(self):
            """!
           Gets the barcode type Value: The type information of the recognized barcode
            """
            return DecodeType(self.getJavaClass().getCodeType())

      def getCodeTypeName(self):
            """!
            Gets the name of the barcode type Value: The type name of the recognized barcode
            """
            return str(self.getJavaClass().getCodeTypeName())

      def getRegion(self):
            """!
            Gets the barcode region Value: The region of the recognized barcode
            """
            return self.region

      def getExtended(self):
            """!
           Gets extended parameters of recognized barcode Value: The extended parameters of recognized barcode
            """
            return self.extended

      def equals(self, other):
            """!
           Returns a value indicating whether this instance is equal to a specified BarCodeResult value.
           :param: other An BarCodeResult value to compare to this instance.
           :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(other.getJavaClass())

      def hashCode(self):
            """!
           Returns the hash code for this instance.
           :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
            Returns a human-readable string representation of this BarCodeResult.
            :return: A string that represents this BarCodeResult.
            """
            return self.getJavaClass().toString()

      def deepClone(self):
            """!
             Creates a copy of BarCodeResult class.
            :return: Returns copy of BarCodeResult class.
            """
            return BarCodeResult(self)


class BarCodeRegionParameters(Assist.BaseJavaClass):
      """!
     Represents the recognized barcode's region and barcode angle
    This sample shows how to get barcode Angle and bounding quadrangle values
    \code
           generator = BarcodeGenerator(EncodeTypes.Code128, "12345")
           generator.save("test.png")
           reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
           for result in reader.readBarCodes():
             print("BarCode CodeText: " + result.getCodeText())
             print("BarCode Angle: " + result.getRegion().getAngle())
             print("BarCode Quadrangle: " + result.getRegion().getQuadrangle())
     \endcode
      """

      def __init__(self, javaClass):
            self.quad = None
            self.rect = None
            self.points = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.quad = Quadrangle.construct(self.getJavaClass().getQuadrangle())
            self.rect = Assist.Rectangle.construct(self.getJavaClass().getRectangle())
            self.points = BarCodeRegionParameters.convertJavaPoints(self.getJavaClass().getPoints())
            # TODO: Implement init() method.

      def convertJavaPoints(javaPoints):
            points = []
            i = 0
            while (i < javaPoints.length):
                  points.append(Assist.Point(javaPoints[i].getX(), javaPoints[i].getY()))
                  i += 1

            return points

      def getQuadrangle(self):
            """!
           Gets Quadrangle bounding barcode region Value: Returns Quadrangle bounding barcode region
            """
            return self.quad

      def getAngle(self):
            """!
           Gets the angle of the barcode (0-360). Value: The angle for barcode (0-360).
            """
            return self.getJavaClass().getAngle()

      def getPoints(self):
            """!
           Gets Points array bounding barcode region Value: Returns Points array bounding barcode region
            """
            return self.points

      def getRectangle(self):
            """!
            Gets Rectangle bounding barcode region Value: Returns Rectangle bounding barcode region
            """
            return self.rect

      def equals(self, obj):
            """!
            Returns a value indicating whether this instance is equal to a specified BarCodeRegionParameters value.
            :param: obj An System.Object value to compare to this instance.
            :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
           Returns the hash code for this instance.
           :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this BarCodeRegionParameters.
           :return: A string that represents this BarCodeRegionParameters.
            """
            return self.getJavaClass().toString()


class BarCodeExtendedParameters(Assist.BaseJavaClass):

      def __init__(self, javaClass):
            self._oneDParameters = None
            self._code128Parameters = None
            self._qrParameters = None
            self._pdf417Parameters = None
            self._dataBarParameters = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self._oneDParameters = OneDExtendedParameters(self.getJavaClass().getOneD())
            self._code128Parameters = Code128ExtendedParameters(self.getJavaClass().getCode128())
            self._qrParameters = QRExtendedParameters(self.getJavaClass().getQR())
            self._pdf417Parameters = Pdf417ExtendedParameters(self.getJavaClass().getPdf417())
            self._dataBarParameters = DataBarExtendedParameters(self.getJavaClass().getDataBar())

      def getDataBar(self):
            """!
           Gets a DataBar additional information<see cref="DataBarExtendedParameters"/> of recognized barcode
           :return: mixed A DataBar additional information<see cref="DataBarExtendedParameters"/> of recognized barcode
            """
            return self._dataBarParameters

      def getOneD(self):
            """!
           Gets a special data OneDExtendedParameters of 1D recognized barcode Value: A special data OneDExtendedParameters of 1D recognized barcode
            """
            return self._oneDParameters

      def getCode128(self):
            """!
           Gets a special data Code128ExtendedParameters of Code128 recognized barcode Value: A special data Code128ExtendedParameters of Code128 recognized barcode
            """
            return self._code128Parameters

      def getQR(self):
            """!
           Gets a QR Structured Append information QRExtendedParameters of recognized barcode Value: A QR Structured Append information QRExtendedParameters of recognized barcode
            """
            return self._qrParameters

      def getPdf417(self):
            """!
           Gets a MacroPdf417 metadata information Pdf417ExtendedParameters of recognized barcode Value: A MacroPdf417 metadata information Pdf417ExtendedParameters of recognized barcode
            """
            return self._pdf417Parameters

      def equals(self, obj):
            """!
           Returns a value indicating whether this instance is equal to a specified BarCodeExtendedParameters value.
           :param: obj An System.Object value to compare to this instance.
           :return: true if obj has the same value as this instance otherwise, false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
           Returns the hash code for this instance.
           :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashCode()

      def toString(self):
            """!
           Returns a human-readable string representation of this BarCodeExtendedParameters.
           :return: A string that represents this BarCodeExtendedParameters.
            """
            return self.getJavaClass().toString()


class QualitySettings(Assist.BaseJavaClass):
      """!
     QualitySettings allows to configure recognition quality and speed manually.
     You can quickly set up QualitySettings by embedded presets: HighPerformance, NormalQuality,
     HighQuality, MaxBarCodes or you can manually configure separate options.
     Default value of QualitySettings is NormalQuality.
    This sample shows how to use QualitySettings with BarCodeReader
    \code
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #set high performance mode
          reader.setQualitySettings(QualitySettings.getHighPerformance())
          for result in reader.readBarCodes():
             print("BarCode CodeText: " + result.getCodeText())
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #normal quality mode is set by default
          for result in reader.readBarCodes():
            print("BarCode CodeText: " + result.getCodeText())
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #set high quality mode with low speed recognition
          reader.setQualitySettings(QualitySettings.getHighQuality())
          for result in reader.readBarCodes():
            print("BarCode CodeText: " + result.getCodeText())
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #set max barcodes mode, which tries to find all possible barcodes, even incorrect. The slowest recognition mode
          reader.setQualitySettings(QualitySettings.getMaxBarCodes())
          for result in reader.readBarCodes():
            print("BarCode CodeText: " + result.getCodeText())
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #set high performance mode
          reader.setQualitySettings(QualitySettings.getHighPerformance())
          #set separate options
          reader.getQualitySettings().setAllowMedianSmoothing(true)
          reader.getQualitySettings().setMedianSmoothingWindowSize(5)
          for result in reader.readBarCodes():
              print("BarCode CodeText: " + result.getCodeText())
          reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
          #default mode is NormalQuality
          #set separate options
          reader.getQualitySettings().setAllowMedianSmoothing(true)
          reader.getQualitySettings().setMedianSmoothingWindowSize(5)
          for result in reader.readBarCodes():
            print("BarCode CodeText: " + result.getCodeText())
   \endcode
      """

      javaClassName = "com.aspose.mw.barcode.recognition.MwQualitySettings"

      def __init__(self, qualitySettings):
            self.detectorSettings = None
            super().__init__(self.initQualitySettings(qualitySettings))
            if (isinstance(qualitySettings, QualitySettings)):
                  self.applyAll(qualitySettings)
            self.init()

      @staticmethod
      def initQualitySettings(qualitySettings):
            if (isinstance(qualitySettings, QualitySettings) | (qualitySettings == None)):
                  java_link = jpype.JClass(QualitySettings.javaClassName)
                  javaQualitySettings = java_link()
                  return javaQualitySettings
            else:
                  return qualitySettings

      def init(self):
            self.detectorSettings = BarcodeSvmDetectorSettings(self.getJavaClass().getDetectorSettings())

      @staticmethod
      def getHighPerformance():
            """!
           HighPerformance recognition quality preset. High quality barcodes are recognized well in this mode.
           \code
                 reader = BarCodeReader("test.png")
                 reader.setQualitySettings(QualitySettings.getHighPerformance())
           \ebdcode
           Value:
          HighPerformance recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getHighPerformance())

      @staticmethod
      def getNormalQuality():
            """!
           NormalQuality recognition quality preset. Suitable for the most of barcodes
           \code
                reader = BarCodeReader("test.png")
                reader.setQualitySettings(QualitySettings.getNormalQuality())
          \endcode
           Value:
          NormalQuality recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getNormalQuality())

      @staticmethod
      def getHighQualityDetection():
            """!
           HighQualityDetection recognition quality preset. Same as NormalQuality but with high quality DetectorSettings
           \code
                 reader = BarCodeReader("test.png")
                 reader.setQualitySettings(QualitySettings.getHighQualityDetection())
           \endcode
           Value:
          HighQualityDetection recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getHighQualityDetection())

      @staticmethod
      def getMaxQualityDetection():
            """!
           MaxQualityDetection recognition quality preset. Same as NormalQuality but with highest quality DetectorSettings.
           Allows to detect diagonal and damaged barcodes.
           \code
                 reader = BarCodeReader("test.png")
                 reader.setQualitySettings(QualitySettings.getMaxQualityDetection())
           \endcode
           Value:
          MaxQualityDetection recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getMaxQualityDetection())

      @staticmethod
      def getHighQuality():
            """!
           HighQuality recognition quality preset. This preset is developed for low quality barcodes.
           \code
                 reader = BarCodeReader("test.png")
                 reader.setQualitySettings(QualitySettings.getHighQuality())
           \endcode
           Value:
          HighQuality recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getHighQuality())

      @staticmethod
      def getMaxBarCodes():
            """!
                 MaxBarCodes recognition quality preset.
                 This preset is developed to recognize all possible barcodes, even incorrect barcodes.
                  \code
                  reader = BarCodeReader("test.png")
                  reader.setQualitySettings(QualitySettings.getMaxBarCodes())
                  \endcode
                 Value:
                MaxBarCodes recognition quality preset.
            """
            java_link = jpype.JClass(QualitySettings.javaClassName)
            JavaQualitySettings = java_link()
            return QualitySettings(JavaQualitySettings.getMaxBarCodes())

      def getAllowInvertImage(self):
            """!
                 Allows engine to recognize inverse color image as additional scan. Mode can be used when barcode is white on black background.
                 Value:
                 Allows engine to recognize inverse color image.
            """
            return self.getJavaClass().getAllowInvertImage()

      def setAllowInvertImage(self, value):
            """!
                 Allows engine to recognize inverse color image as additional scan. Mode can be used when barcode is white on black background.
                 Value:
                 Allows engine to recognize inverse color image.
            """
            self.getJavaClass().setAllowInvertImage(value)

      def getAllowIncorrectBarcodes(self):
            """!
                 Allows engine to recognize barcodes which has incorrect checksumm or incorrect values.
                Mode can be used to recognize damaged barcodes with incorrect text.
                 Value:
                 Allows engine to recognize incorrect barcodes.
            """
            return self.getJavaClass().getAllowIncorrectBarcodes()

      def setAllowIncorrectBarcodes(self, value):
            """!
                 Allows engine to recognize barcodes which has incorrect checksumm or incorrect values.
                Mode can be used to recognize damaged barcodes with incorrect text.
                 Value:
                 Allows engine to recognize incorrect barcodes.
            """
            self.getJavaClass().setAllowIncorrectBarcodes(value)

      def getReadTinyBarcodes(self):
            """!
           Allows engine to recognize tiny barcodes on large images. Ignored if AllowIncorrectBarcodes is set to True.

           Default value: False.

          :return: If True, allows engine to recognize tiny barcodes on large images.
            """
            return self.getJavaClass().getReadTinyBarcodes()

      def setReadTinyBarcodes(self, value):
            """!
                 Allows engine to recognize tiny barcodes on large images. Ignored if AllowIncorrectBarcodes is set to True.

                 Default value: False.

                 :param: value If True, allows engine to recognize tiny barcodes on large images.
            """
            self.getJavaClass().setReadTinyBarcodes(value)

      def getCheckMore1DVariants(self):
            """!
                 Allows engine to recognize 1D barcodes with checksum by checking more recognition variants. Default value: False.
                 :return: If True, allows engine to recognize 1D barcodes with checksum.
            """
            return self.getJavaClass().getCheckMore1DVariants()

      def setCheckMore1DVariants(self, value):
            """!
                Allows engine to recognize 1D barcodes with checksum by checking more recognition variants. Default value: False.
                :param value If True, allows engine to recognize 1D barcodes with checksum.
            """
            self.getJavaClass().setCheckMore1DVariants(value)

      def getAllowComplexBackground(self):
            """!
                 Allows engine to recognize color barcodes on color background as additional scan. Extremely slow mode.
                 Value:
                Allows engine to recognize color barcodes on color background.
            """
            return self.getJavaClass().getAllowComplexBackground()

      def setAllowComplexBackground(self, value):
            """!
                 Allows engine to recognize color barcodes on color background as additional scan. Extremely slow mode.
                 Value:v
                Allows engine to recognize color barcodes on color background.
            """
            self.getJavaClass().setAllowComplexBackground(value)

      def getAllowMedianSmoothing(self):
            """!
                 Allows engine to enable median smoothing as additional scan. Mode helps to recognize noised barcodes.
                 Value:
                Allows engine to enable median smoothing.
            """
            return self.getJavaClass().getAllowMedianSmoothing()

      def setAllowMedianSmoothing(self, value):
            """!
                Allows engine to enable median smoothing as additional scan. Mode helps to recognize noised barcodes.
                 Value:
                Allows engine to enable median smoothing.
            """
            self.getJavaClass().setAllowMedianSmoothing(value)

      def getMedianSmoothingWindowSize(self):
            """!
                Window size for median smoothing. Typical values are 3 or 4. Default value is 3. AllowMedianSmoothing must be set.
                 Value:
                Window size for median smoothing.
            """
            return self.getJavaClass().getMedianSmoothingWindowSize()

      def setMedianSmoothingWindowSize(self, value):
            """!
                Window size for median smoothing. Typical values are 3 or 4. Default value is 3. AllowMedianSmoothing must be set.
                 Value:
                Window size for median smoothing.
            """
            self.getJavaClass().setMedianSmoothingWindowSize(value)

      def getAllowRegularImage(self):
            """!
                 Allows engine to recognize regular image without any restorations as main scan. Mode to recognize image as is.
                 Value:
                Allows to recognize regular image without any restorations.
            """
            return self.getJavaClass().getAllowRegularImage()

      def setAllowRegularImage(self, value):
            """!
                 Allows engine to recognize regular image without any restorations as main scan. Mode to recognize image as is.
                 Value:
                Allows to recognize regular image without any restorations.
            """
            self.getJavaClass().setAllowRegularImage(value)

      def getAllowDecreasedImage(self):
            """!
               Allows engine to recognize decreased image as additional scan. Size for decreasing is selected by internal engine algorithms.
                Mode helps to recognize barcodes which are noised and blurred but captured with high resolution.
                 Value:
                Allows engine to recognize decreased image
            """
            return self.getJavaClass().getAllowDecreasedImage()

      def setAllowDecreasedImage(self, value):
            """!
                 Allows engine to recognize decreased image as additional scan. Size for decreasing is selected by internal engine algorithms.
                Mode helps to recognize barcodes which are noised and blurred but captured with high resolution.
                 Value:
                Allows engine to recognize decreased image
            """
            self.getJavaClass().setAllowDecreasedImage(value)

      def getAllowWhiteSpotsRemoving(self):
            """!
                Allows engine to recognize image without small white spots as additional scan. Mode helps to recognize noised image as well as median smoothing filtering.
                 Value:
                Allows engine to recognize image without small white spots.
            """
            return self.getJavaClass().getAllowWhiteSpotsRemoving()

      def setAllowWhiteSpotsRemoving(self, value):
            """!
                 Allows engine to recognize image without small white spots as additional scan. Mode helps to recognize noised image as well as median smoothing filtering.
                 Value:
                 Allows engine to recognize image without small white spots.
            """
            self.getJavaClass().setAllowWhiteSpotsRemoving(value)

      def getAllowOneDAdditionalScan(self):
            """!
                 Allows engine for 1D barcodes to recognize regular image with different params as additional scan. Mode helps to recongize low height 1D barcodes.
                 Value:
                Allows engine for 1D barcodes to run additional scan.
            """
            return self.getJavaClass().getAllowOneDAdditionalScan()

      def setAllowOneDAdditionalScan(self, value):
            """!
                 Allows engine for 1D barcodes to recognize regular image with different params as additional scan. Mode helps to recongize low height 1D barcodes.
                 Value:
                 Allows engine for 1D barcodes to run additional scan.
            """
            self.getJavaClass().setAllowOneDAdditionalScan(value)

      def getAllowOneDFastBarcodesDetector(self):
            """!
                 Allows engine for 1D barcodes to quickly recognize high quality barcodes which fill almost whole image.
                Mode helps to quickly recognize generated barcodes from Internet.
                 Value:
                Allows engine for 1D barcodes to quickly recognize high quality barcodes.
            """
            return self.getJavaClass().getAllowOneDFastBarcodesDetector()

      def setAllowOneDFastBarcodesDetector(self, value):
            """!
                 Allows engine for 1D barcodes to quickly recognize high quality barcodes which fill almost whole image.
                 Mode helps to quickly recognize generated barcodes from Internet.
                 Value:
                Allows engine for 1D barcodes to quickly recognize high quality barcodes.
            """
            self.getJavaClass().setAllowOneDFastBarcodesDetector(value)

      def getAllowMicroWhiteSpotsRemoving(self):
            """!
                 Allows engine for Postal barcodes to recognize slightly noised images. Mode helps to recognize sligtly damaged Postal barcodes.
                 Value:
                 Allows engine for Postal barcodes to recognize slightly noised images.
            """
            return self.getJavaClass().getAllowMicroWhiteSpotsRemoving()

      def setAllowMicroWhiteSpotsRemoving(self, value):
            """!
                 Allows engine for Postal barcodes to recognize slightly noised images. Mode helps to recognize sligtly damaged Postal barcodes.
                 Value:
                 Allows engine for Postal barcodes to recognize slightly noised images.
            """
            self.getJavaClass().setAllowMicroWhiteSpotsRemoving(value)

      def getFastScanOnly(self):
            """
            Allows engine for 1D barcodes to quickly recognize middle slice of an image and return result without using any time-consuming algorithms.
            :return: Allows engine for 1D barcodes to quickly recognize high quality barcodes.
            """
            return self.getJavaClass().getFastScanOnly()

      def setFastScanOnly(self, value):
            """
            Allows engine for 1D barcodes to quickly recognize middle slice of an image and return result without using any time-consuming algorithms.
            :param value: Allows engine for 1D barcodes to quickly recognize high quality barcodes.
            """
            self.getJavaClass().setFastScanOnly(value)

      def getAllowSaltAndPaperFiltering(self):
            """!
                 Allows engine to recognize barcodes with salt and paper noise type. Mode can remove small noise with white and black dots.
                 Value:
                 Allows engine to recognize barcodes with salt and paper noise type.
            """
            return self.getJavaClass().getAllowSaltAndPaperFiltering()

      def setAllowSaltAndPaperFiltering(self, value):
            """!
                  Allows engine to recognize barcodes with salt and paper noise type. Mode can remove small noise with white and black dots.
                 Value:
                 Allows engine to recognize barcodes with salt and paper noise type.
            """
            self.getJavaClass().setAllowSaltAndPaperFiltering(value)

      def getAllowDetectScanGap(self):
            """!
                 Allows engine to use gap between scans to increase recognition speed. Mode can make recognition problems with low height barcodes.
                 Value:
                 Allows engine to use gap between scans to increase recognition speed.
            """
            return self.getJavaClass().getAllowDetectScanGap()

      def setAllowDetectScanGap(self, value):
            """!
                 Allows engine to use gap between scans to increase recognition speed. Mode can make recognition problems with low height barcodes.
                 Value:
                 Allows engine to use gap between scans to increase recognition speed.
            """
            self.getJavaClass().setAllowDetectScanGap(value)

      def getAllowDatamatrixIndustrialBarcodes(self):
            """!
                 Allows engine for Datamatrix to recognize dashed industrial Datamatrix barcodes.
                Slow mode which helps only for dashed barcodes which consist from spots.
                 Value:
                Allows engine for Datamatrix to recognize dashed industrial barcodes.
            """
            return self.getJavaClass().getAllowDatamatrixIndustrialBarcodes()

      def setAllowDatamatrixIndustrialBarcodes(self, value):
            """!
                 Allows engine for Datamatrix to recognize dashed industrial Datamatrix barcodes.
                Slow mode which helps only for dashed barcodes which consist from spots.
                 Value:
                Allows engine for Datamatrix to recognize dashed industrial barcodes.
            """
            self.getJavaClass().setAllowDatamatrixIndustrialBarcodes(value)

      def getAllowQRMicroQrRestoration(self):
            """!
                 Allows engine for QR/MicroQR to recognize damaged MicroQR barcodes.
                 Value:
                Allows engine for QR/MicroQR to recognize damaged MicroQR barcodes.
            """
            return self.getJavaClass().getAllowQRMicroQrRestoration()

      def setAllowQRMicroQrRestoration(self, value):
            """!
                 Allows engine for QR/MicroQR to recognize damaged MicroQR barcodes.
                 Value:
                 Allows engine for QR/MicroQR to recognize damaged MicroQR barcodes.
            """
            self.getJavaClass().setAllowQRMicroQrRestoration(value)

      def getAllowOneDWipedBarsRestoration(self):
            """!
                  Allows engine for 1D barcodes to recognize barcodes with single wiped/glued bars in pattern.
                 Value:
                 Allows engine for 1D barcodes to recognize barcodes with single wiped/glued bars in pattern.
            """
            return self.getJavaClass().getAllowOneDWipedBarsRestoration()

      def setAllowOneDWipedBarsRestoration(self, value):
            """!
                 Allows engine for 1D barcodes to recognize barcodes with single wiped/glued bars in pattern.
                 Value:
                 Allows engine for 1D barcodes to recognize barcodes with single wiped/glued bars in pattern.
            """
            self.getJavaClass().setAllowOneDWipedBarsRestoration(value)

      def getDetectorSettings(self):
            """!
            Barcode detector settings.
            """
            return self.detectorSettings

      def setDetectorSettings(self, value):
            """!
            Barcode detector settings.
            """
            self.getJavaClass().setDetectorSettings(value)
            self.detectorSettings = value

      def applyAll(self, Src):
            """!
            apply all values from Src setting to this
            :param: Src source settings
            """
            self.setAllowInvertImage(Src.getAllowInvertImage())
            self.setAllowIncorrectBarcodes(Src.getAllowIncorrectBarcodes())
            self.setAllowComplexBackground(Src.getAllowComplexBackground())
            self.setAllowMedianSmoothing(Src.getAllowMedianSmoothing())
            self.setMedianSmoothingWindowSize(Src.getMedianSmoothingWindowSize())
            self.setAllowRegularImage(Src.getAllowRegularImage())
            self.setAllowDecreasedImage(Src.getAllowDecreasedImage())
            self.setAllowWhiteSpotsRemoving(Src.getAllowWhiteSpotsRemoving())
            self.setAllowOneDAdditionalScan(Src.getAllowOneDAdditionalScan())
            self.setAllowOneDFastBarcodesDetector(Src.getAllowOneDFastBarcodesDetector())
            self.setAllowMicroWhiteSpotsRemoving(Src.getAllowMicroWhiteSpotsRemoving())
            self.setAllowSaltAndPaperFiltering(Src.getAllowSaltAndPaperFiltering())
            self.setAllowDetectScanGap(Src.getAllowDetectScanGap())


class Code128DataPortion(Assist.BaseJavaClass):
      """!
     Contains the data of subtype for Code128 type barcode
      """
      javaClassName = "com.aspose.mw.barcode.recognition.MwCode128DataPortion"

      def __init__(self, code128SubType, data):
            """!
            Creates a new instance of the {@code Code128DataPortion} class with start code symbol and decoded codetext.
            :param: code128SubType A start encoding symbol
            :param: data A partial codetext
            """
            java_link = jpype.JClass(self.javaClassName)
            if isinstance(code128SubType, Code128SubType):
                  code128DataPortion = java_link(str(code128SubType.value), data)
            else:
                  code128DataPortion = java_link(str(code128SubType), data)

            super().__init__(code128DataPortion)
            self.init()

      def construct(javaClass):
            code128DataPortion = Code128DataPortion(0, "")
            code128DataPortion.setJavaClass(javaClass)
            return code128DataPortion

      def getData(self):
            """!
            Gets the part of code text related to subtype.
           :return: The part of code text related to subtype
            """
            return self.getJavaClass().getData()

      def setData(self, value):
            """!
            Gets the part of code text related to subtype.
           :return: The part of code text related to subtype
            """
            self.getJavaClass().setData(value)

      def getCode128SubType(self):
            """!
           Gets the type of Code128 subset
           :return: The type of Code128 subset
            """
            return self.getJavaClass().getCode128SubType()

      def setCode128SubType(self, value):
            """!
           Gets the type of Code128 subset
           :return: The type of Code128 subset
            """
            self.getJavaClass().setCode128SubType(value)

      def init(self):
            return
            # TODO

      def toString(self):
            """!
           Returns a human-readable string representation of this {@code Code128DataPortion}.
           :return: A string that represents this {@code Code128DataPortion}.
            """
            return self.getJavaClass().toString()


class DataBarExtendedParameters(Assist.BaseJavaClass):
      """!
    Stores a DataBar additional information of recognized barcode
    BarCodeReader reader = new BarCodeReader("c:\\test.png", DecodeType.DATABAR_OMNI_DIRECTIONAL)
    \code
    for result in reader.readBarCodes():
       print("BarCode Type: " + result.getCodeTypeName())
       print("BarCode CodeText: " + result.getCodeText())
       print("QR Structured Append Quantity: " + result.getExtended().getQR().getQRStructuredAppendModeBarCodesQuantity())
    \endcode
      """

      javaClassName = "com.aspose.mw.barcode.recognition.MwDataBarExtendedParameters"

      def init(self):
            pass

      def is2DCompositeComponent(self):
            """!
          Gets the DataBar 2D composite component flag. Default value is false.
          :return: The DataBar 2D composite component flag.
            """
            return self.getJavaClass().is2DCompositeComponent()

      def equals(self, obj):
            """!
           Returns a value indicating whether this instance is equal to a specified <see cref="DataBarExtendedParameters"/> value.
           :param: obj An System.Object value to compare to this instance.
           :return: <b>true</b> if obj has the same value as this instance; otherwise, <b>false</b>.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashcode(self):
            """!
            Returns the hash code for this instance.
           :return: A 32-bit signed integer hash code.
            """
            return self.getJavaClass().hashcode()

      def toString(self):
            """!
            Returns a human-readable string representation of this <see cref="DataBarExtendedParameters"/>.
           :return: A string that represents this <see cref="DataBarExtendedParameters"/>.
            """
            return self.getJavaClass().toString()

class AustraliaPostSettings(Assist.BaseJavaClass):
      """!
      AustraliaPost decoding parameters. Contains parameters which make influence on recognized data of AustraliaPost symbology.
      """
      javaClassName = "com.aspose.mw.barcode.recognition.MwAustraliaPostSettings"

      def init(self):
            pass

      def __init__(self, settings):
            """!
            AustraliaPostSettings constructor
            :param settings:
            """
            if settings != None:
                  super().__init__(settings.getJavaClass())
            else:


                  java_link = jpype.JClass(self.javaClassName)
                  australiaPostSettings = java_link()
                  super().__init__(australiaPostSettings)


      @staticmethod
      def construct(javaClass):
            australiaPostSettings = AustraliaPostSettings(None)
            australiaPostSettings.setJavaClass(javaClass)
            return australiaPostSettings

      def getCustomerInformationInterpretingType(self):
            """!
            Gets the Interpreting Type for the Customer Information of AustralianPost BarCode.DEFAULT is CustomerInformationInterpretingType.OTHER.
            :return: The interpreting type (CTable, NTable or Other) of customer information for AustralianPost BarCode
            """
            return CustomerInformationInterpretingType(self.getJavaClass().getCustomerInformationInterpretingType())

      def setCustomerInformationInterpretingType(self, value):
            """!
            Sets the Interpreting Type for the Customer Information of AustralianPost BarCode.DEFAULT is CustomerInformationInterpretingType.OTHER.
            :param value: The interpreting type (CTable, NTable or Other) of customer information for AustralianPost BarCode
            """
            self.getJavaClass().setCustomerInformationInterpretingType(value.value)

      def getIgnoreEndingFillingPatternsForCTable(self):
            """!
            The flag which force AustraliaPost decoder to ignore last filling patterns in Customer Information Field during decoding as CTable method.
            CTable encoding method does not have any gaps in encoding table and sequnce "333" of filling paterns is decoded as letter "z".

            Example

            generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "5912345678AB")
            generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.C_TABLE)
            image = generator.generateBarCodeImage(BarcodeImageFormat.PNG)
            reader = new BarCodeReader(image, None, DecodeType.AUSTRALIA_POST)
            reader.getBarcodeSettings().getAustraliaPost().setCustomerInformationInterpretingType(CustomerInformationInterpretingType.C_TABLE)
            reader.getBarcodeSettings().getAustraliaPost().setIgnoreEndingFillingPatternsForCTable(true)
            for result in reader.readBarCodes():
                print("BarCode Type: " +result.getCodeType())
                print("BarCode CodeText: " +result.getCodeText())

            :return: The flag which force AustraliaPost decoder to ignore last filling patterns during CTable method decoding
            """
            return self.getJavaClass().getIgnoreEndingFillingPatternsForCTable()

      def setIgnoreEndingFillingPatternsForCTable(self, value):
            self.getJavaClass().setIgnoreEndingFillingPatternsForCTable(value)

class BarcodeSettings(Assist.BaseJavaClass):

      javaClassName ="com.aspose.mw.barcode.recognition.MwBarcodeSettings"

      def __init__(self, settings):
            """!
            BarcodeSettings copy constructor
            :param settings: settings The source of the data
            """
            self._australiaPost = None
            if settings != None:
                  super().__init__(settings.getJavaClass())
            else:
                  java_link = jpype.JClass(self.javaClassName)
                  barcodeSettings = java_link()
                  super().__init__(barcodeSettings)

      @staticmethod
      def construct(javaClass):
            """!
            BarcodeSettings copy constructor
            :param settings The source of the data
            """
            barcodeSettings = BarcodeSettings(None)
            barcodeSettings.setJavaClass(javaClass)
            return barcodeSettings

      def init(self):
            self._australiaPost = AustraliaPostSettings.construct(self.getJavaClass().getAustraliaPost())

      def getChecksumValidation(self):
            """!
            Enable checksum validation during recognition for 1D and Postal barcodes.
            Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.
            Checksum never used: Codabar, PatchCode, Pharmacode, DataLogic2of5
            Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, ItalianPost25, Matrix2of5, MSI, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN
            Checksum always used: Rest symbologies

            Example

            \code
            generator = new BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
            generator.save("c:/test.png", BarcodeImageFormat.PNG)
            reader = new BarCodeReader("c:/test.png", DecodeType.EAN_13)
            //checksum disabled
            reader.getBarcodeSettings().setChecksumValidation(ChecksumValidation.OFF)
            for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())
                 print ("BarCode Value: " + result.getExtended().getOneD().getValue())
                 print ("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())

            reader = new BarCodeReader(@"c:\test.png", DecodeType.EAN_13)
            //checksum enabled
            reader.getBarcodeSettings().setChecksumValidation(ChecksumValidation.ON)
            for result in reader.readBarCodes():
                 print ("BarCode CodeText: " + result.CodeText)
                 print ("BarCode Value: " + result.getExtended().getOneD().getValue())
                 print ("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())

            \endcode
            :return:Enable checksum validation during recognition for 1D and Postal barcodes.
            """
            return ChecksumValidation(self.getJavaClass().getChecksumValidation())

      def setChecksumValidation(self, value):
            """
            Enable checksum validation during recognition for 1D and Postal barcodes.
            Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.
            Checksum never used: Codabar, PatchCode, Pharmacode, DataLogic2of5
            Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, ItalianPost25, Matrix2of5, MSI, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN
            Checksum always used: Rest symbologies

            Example

            \code
            generator = new BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
            generator.save("c:/test.png", BarcodeImageFormat.PNG)
            reader = new BarCodeReader("c:/test.png", DecodeType.EAN_13)
            //checksum disabled
            reader.getBarcodeSettings().setChecksumValidation(ChecksumValidation.OFF)
            for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())
                 print ("BarCode Value: " + result.getExtended().getOneD().getValue())
                 print ("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())

            reader = new BarCodeReader(@"c:\test.png", DecodeType.EAN_13)
            //checksum enabled
            reader.getBarcodeSettings().setChecksumValidation(ChecksumValidation.ON)
           for result in reader.readBarCodes():
                 print ("BarCode CodeText: " + result.CodeText)
                 print ("BarCode Value: " + result.getExtended().getOneD().getValue())
                 print ("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())

            \endcode
            :param value: Enable checksum validation during recognition for 1D and Postal barcodes.
            """
            self.getJavaClass().setChecksumValidation(value.value)

      def getStripFNC(self):
            """

            Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.

            Example

            \code
            generator = new BarcodeGenerator(EncodeTypes.GS_1_CODE_128, "(02)04006664241007(37)1(400)7019590754")
            generator.save("c:/test.png", BarcodeImageFormat.PNG)
            reader = new BarCodeReader("c:/test.png", DecodeType.CODE_128)

            //StripFNC disabled
            reader.getBarcodeSettings().setStripFNC(false)
            for result in reader.readBarCodes():
                print ("BarCode CodeText: " +result.getCodeText())

            reader = new BarCodeReader("c:/test.png", DecodeType.CODE_128)

            //StripFNC enabled
            reader.getBarcodeSettings().setStripFNC(true)
            for result in reader.readBarCodes():
                print ("BarCode CodeText: " +result.getCodeText())

            \endcode

            :return: Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.
            """
            return self.getJavaClass().getStripFNC()

      def setStripFNC(self, value):
            """
             Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.

            Example

            \code
             generator = new BarcodeGenerator(EncodeTypes.GS_1_CODE_128, "(02)04006664241007(37)1(400)7019590754")
             generator.save("c:/test.png", BarcodeImageFormat.PNG)
             reader = new BarCodeReader("c:/test.png", DecodeType.CODE_128)

             //StripFNC disabled
             reader.getBarcodeSettings().setStripFNC(false)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())

             reader = new BarCodeReader("c:/test.png", DecodeType.CODE_128)

             //StripFNC enabled
             reader.getBarcodeSettings().setStripFNC(true)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())

             \endcode

             :param: value  Strip FNC1, FNC2, FNC3 characters from codetext. Default value is false.
            """
            self.getJavaClass().setStripFNC(value)

      def getDetectEncoding(self):
            """

             The flag which force engine to detect codetext encoding for Unicode codesets. Default value is true.

             Example

             \code
             generator = new BarcodeGenerator(EncodeTypes.QR, "Слово"))
             im = generator.generateBarcodeImage(BarcodeImageFormat.PNG)

             //detects encoding for Unicode codesets is enabled
             reader = new BarCodeReader(im, DecodeType.QR)
             reader.getBarcodeSettings().setDetectEncoding(true)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())

             //detect encoding is disabled
             reader = new BarCodeReader(im, DecodeType.QR)
             reader.getBarcodeSettings().setDetectEncoding(false)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())
            \endcode

            :return:The flag which force engine to detect codetext encoding for Unicode codesets
            """
            return self.getJavaClass().getDetectEncoding()

      def setDetectEncoding(self, value):
            """
             The flag which force engine to detect codetext encoding for Unicode codesets. Default value is true.

             Example

            \code
             generator = new BarcodeGenerator(EncodeTypes.QR, "Слово"))
             im = generator.generateBarcodeImage(BarcodeImageFormat.PNG)

             //detects encoding for Unicode codesets is enabled
               reader = new BarCodeReader(im, DecodeType.QR)
             reader.getBarcodeSettings().setDetectEncoding(true)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())

             //detect encoding is disabled
             reader = new BarCodeReader(im, DecodeType.QR)
             reader.getBarcodeSettings().setDetectEncoding(false)
             for result in reader.readBarCodes():
                 print ("BarCode CodeText: " +result.getCodeText())
            \endcode

            :param value: The flag which force engine to detect codetext encoding for Unicode codesets
            """
            self.getJavaClass().setDetectEncoding(value)

      def getAustraliaPost(self):
            """
            :return: The AustraliaPost decoding parameters which make influence on recognized data of AustraliaPost symbology
            """
            return self._australiaPost

class RecognitionAbortedException(Exception):

      javaClassName = "com.aspose.mw.barcode.recognition.MwRecognitionAbortedException"

      def getExecutionTime(self):
            """
            Gets the execution time of current recognition session
            :return: The execution time of current recognition session
            """
            return self.javaClass.getExecutionTime()

      def setExecutionTime(self, value):
            """
            Sets the execution time of current recognition session
            :param value: value The execution time of current recognition session
            """
            self.javaClass.setExecutionTime(value)

      def __init__(self, message, executionTime):
            """
            Initializes a new instance of the <see cref="RecognitionAbortedException" /> class with specified recognition abort message.

            :param message: The error message of the exception.
            :param executionTime: The execution time of current recognition session.
            """
            super().__init__(message)
            self.javaClass = None
            java_class_link = jpype.JClass(RecognitionAbortedException.javaClassName)
            if (message != None  and executionTime != None):
                  self.javaClass = java_class_link(message, executionTime)
            elif executionTime != None:
                  self.javaClass = java_class_link(executionTime)
            else:
                  self.javaClass = java_class_link()

      @staticmethod
      def construct(javaClass):
            exception = RecognitionAbortedException(None, None)
            exception.javaClass = javaClass
            return exception

      def init(self):
            pass

class DecodeType(Enum):
      """!
       Specify the type of barcode to read.
       This sample shows how to detect Code39 and Code128 barcodes.
       \code
             reader = BarCodeReader("test.png", None,  [ DecodeType.CODE_39_STANDARD, DecodeType.CODE_128 ])
             for result in reader.readBarCodes():
               print("BarCode Type: " + result.getCodeTypeName())
               print("BarCode CodeText: " + result.getCodeText())
        \endcode
      """

      NONE = -1
      """!
     Unspecified decode type.
      """

      CODABAR = 0
      """!
      Specifies that the data should be decoded with {@code <b>CODABAR</b>} barcode specification
      """

      CODE_11 = 1
      """!
     Specifies that the data should be decoded with {@code <b>CODE 11</b>} barcode specification
      """

      CODE_39_STANDARD = 2
      """!
      Specifies that the data should be decoded with {@code <b>Standard CODE 39</b>} barcode specification
      """

      CODE_39_EXTENDED = 3
      """!
     Specifies that the data should be decoded with {@code <b>Extended CODE 39</b>} barcode specification
      """

      CODE_93_STANDARD = 4
      """!
      Specifies that the data should be decoded with {@code <b>Standard CODE 93</b>} barcode specification
      """

      CODE_93_EXTENDED = 5
      """!
      Specifies that the data should be decoded with {@code <b>Extended CODE 93</b>} barcode specification
      """

      CODE_128 = 6
      """!
      Specifies that the data should be decoded with {@code <b>CODE 128</b>} barcode specification
      """

      GS_1_CODE_128 = 7
      """!
     Specifies that the data should be decoded with {@code <b>GS1 CODE 128</b>} barcode specification
      """

      EAN_8 = 8
      """!
     Specifies that the data should be decoded with {@code <b>EAN-8</b>} barcode specification
      """

      EAN_13 = 9
      """!
      Specifies that the data should be decoded with {@code <b>EAN-13</b>} barcode specification
      """

      EAN_14 = 10
      """!
      Specifies that the data should be decoded with {@code <b>EAN14</b>} barcode specification
      """

      SCC_14 = 11
      """!
      Specifies that the data should be decoded with {@code <b>SCC14</b>} barcode specification
      """

      SSCC_18 = 12
      """!
      Specifies that the data should be decoded with {@code <b>SSCC18</b>} barcode specification
      """

      UPCA = 13
      """!
     Specifies that the data should be decoded with {@code <b>UPC-A</b>} barcode specification
      """

      UPCE = 14
      """!
      Specifies that the data should be decoded with {@code <b>UPC-E</b>} barcode specification
      """

      ISBN = 15
      """!
     Specifies that the data should be decoded with {@code <b>ISBN</b>} barcode specification
      """

      STANDARD_2_OF_5 = 16
      """!
      Specifies that the data should be decoded with {@code <b>Standard 2 of 5</b>} barcode specification
      """

      INTERLEAVED_2_OF_5 = 17
      """!
      Specifies that the data should be decoded with {@code <b>INTERLEAVED 2 of 5</b>} barcode specification
      """

      MATRIX_2_OF_5 = 18
      """!
      Specifies that the data should be decoded with {@code <b>Matrix 2 of 5</b>} barcode specification
      """

      ITALIAN_POST_25 = 19
      """!
      Specifies that the data should be decoded with {@code <b>Italian Post 25</b>} barcode specification
      """

      IATA_2_OF_5 = 20
      """!
      Specifies that the data should be decoded with {@code <b>IATA 2 of 5</b>} barcode specification. IATA (International Air Transport Association) uses this barcode for the management of air cargo.
      """

      ITF_14 = 21
      """!
      Specifies that the data should be decoded with {@code <b>ITF14</b>} barcode specification
      """

      ITF_6 = 22
      """!
     Specifies that the data should be decoded with {@code <b>ITF6</b>} barcode specification
      """

      MSI = 23
      """!
     Specifies that the data should be decoded with {@code <b>MSI Plessey</b>} barcode specification
      """

      VIN = 24
      """!
     Specifies that the data should be decoded with {@code <b>VIN</b>} (Vehicle Identification Number) barcode specification
      """

      DEUTSCHE_POST_IDENTCODE = 25
      """!
      Specifies that the data should be decoded with {@code <b>DeutschePost Ident code</b>} barcode specification
      """

      DEUTSCHE_POST_LEITCODE = 26
      """!
      Specifies that the data should be decoded with {@code <b>DeutschePost Leit code</b>} barcode specification
      """

      OPC = 27
      """!
      Specifies that the data should be decoded with {@code <b>OPC</b>} barcode specification
      """

      PZN = 28
      """!
      Specifies that the data should be decoded with {@code <b>PZN</b>} barcode specification. This symbology is also known as Pharma Zentral Nummer
      """

      PHARMACODE = 29
      """!
      Specifies that the data should be decoded with {@code <b>Pharmacode</b>} barcode. This symbology is also known as Pharmaceutical BINARY Code
      """

      DATA_MATRIX = 30
      """!
       Specifies that the data should be decoded with {@code <b>DataMatrix</b>} barcode symbology
      """

      GS_1_DATA_MATRIX = 31
      """!
     Specifies that the data should be decoded with {@code <b>GS1DataMatrix</b>} barcode symbology
      """

      QR = 32
      """!
      Specifies that the data should be decoded with {@code <b>QR Code</b>} barcode specification
      """

      AZTEC = 33
      """!
      Specifies that the data should be decoded with {@code <b>Aztec</b>} barcode specification
      """

      PDF_417 = 34
      """!
      Specifies that the data should be decoded with {@code <b>Pdf417</b>} barcode symbology
      """

      MACRO_PDF_417 = 35
      """!
     Specifies that the data should be decoded with {@code <b>MacroPdf417</b>} barcode specification
      """

      MICRO_PDF_417 = 36
      """!
     Specifies that the data should be decoded with {@code <b>MicroPdf417</b>} barcode specification
      """

      CODABLOCK_F = 65
      """!
      Specifies that the data should be decoded with {@code <b>CodablockF</b>} barcode specification
      """

      MAILMARK = 66
      """!
      Specifies that the data should be decoded with <b>Royal Mail Mailmark</b> barcode specification.
      """

      AUSTRALIA_POST = 37
      """!
      Specifies that the data should be decoded with {@code <b>Australia Post</b>} barcode specification
      """

      POSTNET = 38
      """!
      Specifies that the data should be decoded with {@code <b>Postnet</b>} barcode specification
      """

      PLANET = 39
      """!
      Specifies that the data should be decoded with {@code <b>Planet</b>} barcode specification
      """

      ONE_CODE = 40
      """!
      Specifies that the data should be decoded with USPS {@code <b>OneCode</b>} barcode specification
      """

      RM_4_SCC = 41
      """!
      Specifies that the data should be decoded with {@code <b>RM4SCC</b>} barcode specification. RM4SCC (Royal Mail 4-state Customer Code) is used for automated mail sort process in UK.
      """

      DATABAR_OMNI_DIRECTIONAL = 42
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR omni-directional</b>} barcode specification
      """

      DATABAR_TRUNCATED = 43
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR truncated</b>} barcode specification
      """

      DATABAR_LIMITED = 44
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR limited</b>} barcode specification
      """

      DATABAR_EXPANDED = 45
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR expanded</b>} barcode specification
      """

      DATABAR_STACKED_OMNI_DIRECTIONAL = 53
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR stacked omni-directional</b>} barcode specification
      """

      DATABAR_STACKED = 54
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR stacked</b>} barcode specification
      """

      DATABAR_EXPANDED_STACKED = 55
      """!
      Specifies that the data should be decoded with {@code <b>GS1 DATABAR expanded stacked</b>} barcode specification
      """

      PATCH_CODE = 46
      """!
      Specifies that the data should be decoded with {@code <b>Patch code</b>} barcode specification. Barcode symbology is used for automated scanning
      """

      ISSN = 47
      """!
      Specifies that the data should be decoded with {@code <b>ISSN</b>} barcode specification
      """

      ISMN = 48
      """!
      Specifies that the data should be decoded with {@code <b>ISMN</b>} barcode specification
      """

      SUPPLEMENT = 49
      """!
      Specifies that the data should be decoded with {@code <b>Supplement(EAN2 EAN5)</b>} barcode specification
      """

      AUSTRALIAN_POSTE_PARCEL = 50
      """!
      Specifies that the data should be decoded with {@code <b>Australian Post Domestic eParcel Barcode</b>} barcode specification
      """

      SWISS_POST_PARCEL = 51
      """!
      Specifies that the data should be decoded with {@code <b>Swiss Post Parcel Barcode</b>} barcode specification
      """

      CODE_16_K = 52
      """!
       Specifies that the data should be decoded with {@code <b>SCode16K</b>} barcode specification
      """

      MICRO_QR = 56
      """!
      Specifies that the data should be decoded with {@code <b>MicroQR Code</b>} barcode specification
      """

      COMPACT_PDF_417 = 57
      """!
      Specifies that the data should be decoded with {@code <b>CompactPdf417</b>} (Pdf417Truncated) barcode specification
      """

      GS_1_QR = 58
      """!
      Specifies that the data should be decoded with {@code <b>GS1 QR</b>} barcode specification
      """

      MAXI_CODE = 59
      """!
      Specifies that the data should be decoded with {@code <b>MaxiCode</b>} barcode specification
      """

      MICR_E_13_B = 60
      """!
      Specifies that the data should be decoded with {@code <b>MICR E-13B</b>} blank specification
      """

      CODE_32 = 61
      """!
      Specifies that the data should be decoded with {@code <b>Code32</b>} blank specification
      """

      DATA_LOGIC_2_OF_5 = 62
      """!
      Specifies that the data should be decoded with {@code <b>DataLogic 2 of 5</b>} blank specification
      """

      DOT_CODE = 63
      """!
      Specifies that the data should be decoded with {@code <b>DotCode</b>} blank specification
      """

      DUTCH_KIX = 64
      """!
      Specifies that the data should be decoded with {@code <b>DotCode</b>} blank specification
      """

      ALL_SUPPORTED_TYPES = 71
      """!
      Specifies that data will be checked with all available symbologies
      """

      TYPES_1D = 67
      """!
      Specifies that data will be checked with all of  1D  barcode symbologies
      """

      POSTAL_TYPES = 68
      """!
      Specifies that data will be checked with all of  1.5D POSTAL  barcode symbologies, like  Planet, Postnet, AustraliaPost, OneCode, RM4SCC, DutchKIX
      """

      MOST_COMMON_TYPES = 69
      """!
      Specifies that data will be checked with most commonly used symbologies
      """

      TYPES_2D = 70
      """!
      Specifies that data will be checked with all of <b>2D</b> barcode symbologies
      """

      javaClassName = "com.aspose.mw.barcode.recognition.MwDecodeTypeUtils"

      @staticmethod
      def is1D(symbology):
            """!
            Determines if the specified <see cref="BaseDecodeType"/> contains any 1D barcode symbology
            :param symbology: 
            :return: string <b>true</b> if <see cref="BaseDecodeType"/> contains any 1D barcode symbology; otherwise, returns <b>false</b>.
            """
            java_link = jpype.JClass(DecodeType.javaClassName)
            javaClass = java_link()
            return javaClass.is1D(symbology)

      @staticmethod
      def isPostal(symbology):
            """!
            Determines if the specified <see cref="BaseDecodeType"/> contains any Postal barcode symbology
            :param symbology: symbology The <see cref="BaseDecodeType"/> to test
            :return: Returns <b>true</b> if <see cref="BaseDecodeType"/> contains any Postal barcode symbology; otherwise, returns <b>false</b>.
            """
            java_link = jpype.JClass(DecodeType.javaClassName)
            javaClass = java_link()
            return javaClass.isPostal(symbology)

      @staticmethod
      def is2D(symbology):
            """
            Determines if the specified <see cref="BaseDecodeType"/> contains any 2D barcode symbology
            :param symbology: symbology The <see cref="BaseDecodeType"/> to test.
            :return: Returns <b>true</b> if <see cref="BaseDecodeType"/> contains any 2D barcode symbology; otherwise, returns <b>false</b>.
            """
            java_link = jpype.JClass(DecodeType.javaClassName)
            javaClass = java_link()
            return javaClass.is2D(symbology)

      @staticmethod
      def containsAny(decodeType, decodeTypes):
            java_link = jpype.JClass(DecodeType.javaClassName)
            javaClass = java_link()
            return javaClass.containsAny(decodeTypes)


class Code128SubType(Enum):

      CODE_SET_A = 1
      """! ASCII characters 00 to 95 (0–9, A–Z and control codes), special characters, and FNC 1–4 """


      CODE_SET_B = 2
      """!
      ASCII characters 32 to 127 (0–9, A–Z, a–z), special characters, and FNC 1–4
      """

      CODE_SET_C = 3
      """!
        00–99 (encodes two digits with a single code point) and FNC1
      """


class CustomerInformationInterpretingType(Enum):
      """!
       Defines the interpreting type(C_TABLE or N_TABLE) of customer information for AustralianPost BarCode.
      """

      """!
        Use C_TABLE to interpret the customer information. Allows A..Z, a..z, 1..9, space and   sing.
        
              generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "5912345678ABCde")
              generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.C_TABLE)
              image = generator.generateBarCodeImage()
              reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
              reader.setCustomerInformationInterpretingType(CustomerInformationInterpretingType.C_TABLE)
              for result in reader.readBarCodes():
                  print("BarCode Type: " + result.getCodeType())
                  print("BarCode CodeText: " + result.getCodeText())
      """
      C_TABLE = 0


      N_TABLE = 1
      """!
      Use N_TABLE to interpret the customer information. Allows digits.
       \code
         generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "59123456781234567")
         generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.N_TABLE)
         image = generator.generateBarCodeImage()
         reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
         reader.setCustomerInformationInterpretingType(CustomerInformationInterpretingType.N_TABLE)
        for result in reader.readBarCodes():
            print("BarCode Type: " + result.getCodeType())
            print("BarCode CodeText: " + result.getCodeText())
        \endcode    
      """

      OTHER = 2
      """!
        Do not interpret the customer information. Allows 0, 1, 2 or 3 symbol only.
       \code
        generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "59123456780123012301230123")
        generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.OTHER)
        image = generator.generateBarCodeImage()
        reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
        reader.CustomerInformationInterpretingType = CustomerInformationInterpretingType.OTHER)
        for result in reader.readBarCodes():
           print("BarCode Type: " + result.getCodeType())
           print("BarCode CodeText: " + result.getCodeText())
        \endcode   
      """


class BarCodeConfidence(Enum):
      """!
       Contains recognition confidence level

       This sample shows how BarCodeConfidence changed, depending on barcode type
       \code
            #Moderate confidence
            generator = BarcodeGenerator(EncodeTypes.CODE_128, "12345")
            generator.save("test.png")
            reader = BarCodeReader("test.png", None,  [DecodeType.CODE_39_STANDARD, DecodeType.CODE_128])
            for result in reader.readBarCodes():
               print("BarCode Type: " + result.getCodeTypeName())
               print("BarCode CodeText: " + result.getCodeText())
               print("BarCode Confidence: " + result.getConfidence())
               print("BarCode ReadingQuality: " + result.getReadingQuality())
            #Strong confidence
            generator = BarcodeGenerator(EncodeTypes.QR, "12345")
            generator.save("test.png")
            reader = BarCodeReader("test.png", None,  [DecodeType.CODE_39_STANDARD, DecodeType.QR])
            for result in reader.readBarCodes():
                print("BarCode Type: " + result.getCodeTypeName())
                print("BarCode CodeText: " + result.getCodeText())
                print("BarCode Confidence: " + result.getConfidence())
                print("BarCode ReadingQuality: " + result.getReadingQuality())
       \endcode
      """

      NONE = "0"
      """!
         Recognition confidence of barcode where codetext was not recognized correctly or barcode was detected as posible fake
      """

      MODERATE = "80"
      """!
        Recognition confidence of barcode (mostly 1D barcodes) with weak checksumm or even without it. Could contains some misrecognitions in codetext
        or even fake recognitions if  is low
        @see BarCodeResult.ReadingQuality
      """

      STRONG = "100"
      """!
         Recognition confidence which was confirmed with BCH codes like Reed–Solomon. There must not be errors in read codetext or fake recognitions
      """


class ChecksumValidation(Enum):
      """!
      Enable checksum validation during recognition for 1D barcodes.

      Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.

      Checksum never used: Codabar

      Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN

      Checksum always used: Rest symbologies

      This sample shows influence of ChecksumValidation on recognition quality and results
      \code
          generator = BarcodeGenerator(EncodeTypes.EAN_13, "1234567890128")
          generator.save("test.png")
          reader = BarCodeReader("test.png", DecodeType.EAN_13)
          #checksum disabled
          reader.setChecksumValidation(ChecksumValidation.OFF)
          for result in reader.readBarCodes():
             print("BarCode CodeText: " + result.getCodeText())
             print("BarCode Value: " + result.getExtended().getOneD().getValue())
             print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
          reader = BarCodeReader("test.png", DecodeType.EAN_13)
          #checksum enabled
          reader.setChecksumValidation(ChecksumValidation.ON)
          for result in reader.readBarCodes():
             print("BarCode CodeText: " + result.getCodeText())
             print("BarCode Value: " + result.getExtended().getOneD().getValue())
             print("BarCode Checksum: " + result.getExtended().getOneD().getCheckSum())
    \endcode

      """

      DEFAULT = 0
      """!
     If checksum is required by the specification - it will be validated.
      """

      ON = 1
      """!
     Always validate checksum if possible.
      """

      OFF = 2
      """!
    Do not validate checksum.
      """
