import time
from datetime import datetime

import jpype
from . import Assist
from enum import Enum
import base64
import io
from PIL import Image

class BarcodeGenerator(Assist.BaseJavaClass):
      """!
     BarcodeGenerator for backend barcode images generation.

     Supported symbologies:<br>

     1D: <br>
         Codabar, Code11, Code128, Code39Standard, Code39Extended
         Code93Standard, Code93Extended, EAN13, EAN8, Interleaved2of5,
         MSI, Standard2of5, UPCA, UPCE, ISBN, GS1Code128, Postnet, Planet
         EAN14, SCC14, SSCC18, ITF14, SingaporePost ...

     2D:<br>
         Aztec, DataMatrix, PDf417, QR code ...

      This sample shows how to create and save a barcode image.
      \code
          encode_type = EncodeTypes.CODE_128
          generator = BarcodeGenerator($encode_type)
          generator = BarcodeGenerator($encode_type)
          generator = BarcodeGenerator($encode_type)
          generator = BarcodeGenerator($encode_type)
          generator = BarcodeGenerator($encode_type)
          generator.setCodeText("123ABC")
      \endcode
        """
      javaClassName = 'com.aspose.mw.barcode.generation.MwBarcodeGenerator'

      def __init__(self, encodeType, codeText):
            """!
            BarcodeGenerator constructor.
            @param args may take the following combinations of arguments:<br>
            1) Barcode symbology type. Use EncodeTypes class to setup a symbology<br>
            2) type EncodeTypes, Text to be encoded.<br>
            \code
              barcodeGenerator = BarcodeGenerator(EncodeTypes.EAN_14, "332211")
            \endcode
            @throws BarCodeException
            """
            javaBarcodeGenerator = jpype.JClass(self.javaClassName)
            if not isinstance(encodeType, EncodeTypes):
                  raise Assist.BarCodeException("Waiting for EncodeTypes type, but got '" + type(encodeType).__name__ + "'")
            self.javaClass = javaBarcodeGenerator(encodeType.value, codeText)
            self.parameters = None
            super().__init__(self.javaClass)

      @staticmethod
      def construct(javaClass):
            barcodeGenerator = BarcodeGenerator(None, None)
            barcodeGenerator.setJavaClass(javaClass)
            return barcodeGenerator

      def init(self):
            self.parameters = BaseGenerationParameters(self.getJavaClass().getParameters())

      def getParameters(self):
            """! Generation parameters.
            @return BaseGenerationParameters """
            return self.parameters

      def getBarcodeType(self):
            """! Barcode symbology type. """
            return EncodeTypes(self.getJavaClass().getBarcodeType())

      def setBarcodeType(self, value):
            """! Barcode symbology type. """
            self.getJavaClass().setBarcodeType(value.value)

      def generateBarCodeImage(self):
            """!  Generate the barcode image under current settings.
            This sample shows how to create and save a barcode image.
            generator = BarCodeGenerator(EncodeTypes.CODE_128)
            image = generator.generateBarCodeImage()
            @return Pillow Image object of barcode image
            """
            try:
                  bytes = base64.b64decode(str(self.javaClass.generateBarCodeImage(BarCodeImageFormat.PNG.value)))
                  buf = io.BytesIO(bytes)
                  bitmap = Image.open(buf)
                  return bitmap
            except Exception as e:
                  raise Assist.BarCodeException(e)

      def save(self, imagePath, imageFormat):
            """!
            Save barcode image to specific file in specific format.
            @param imagePath Path to save to.
            @param imageFormat Optional format override. If omitted, the format to use is determined from the filename extension. If a file object was used instead of a filename, this parameter should always be used.
            file_path = "img1.png"
            generator = BarCodeGenerator(EncodeTypes.CODE_128)
            generator.save(file_path, "PNG")
            """
            bytes = bytearray(base64.b64decode(str(self.javaClass.generateBarCodeImage(imageFormat.value))))
            file = open(imagePath, "wb")
            file.write(bytes)
            file.close()

      def getCodeText(self):
            """!Text to be encoded."""
            return self.getJavaClass().getCodeText()

      def setCodeText(self, value):
            """! Text to be encoded.  """
            self.getJavaClass().setCodeText(value)

      def exportToXml(self, filePath):
            """
            Exports BarCode properties to the xml-stream specified
            :param resource:  The xml-stream
            :return: Whether or not export completed successfully. Returns <b>True</b> in case of success; <b>False</b> Otherwise
            """
            try:
                  xmlData = self.getJavaClass().exportToXml()
                  isSaved = xmlData != None
                  if isSaved:
                        text_file = open(filePath, "w")
                        text_file.write(xmlData)
                        text_file.close()
                  return isSaved
            except Exception as ex:
                  raise Assist.BarCodeException(ex)

      @staticmethod
      def importFromXml(resource):
            """!
            Imports BarCode properties from the xml-file specified and creates BarcodeGenerator instance.
            :param resource: The name of  the file
            :return: instance
            """
            try:
                  xmlData = BarcodeGenerator.loadFileBase64String(resource)
                  offset = 6
                  xmlData = xmlData.substr(offset)
                  javaBarcodeGenerator = jpype.JClass(BarcodeGenerator.javaClassName)
                  return BarcodeGenerator.construct(javaBarcodeGenerator).importFromXml(xmlData)
            except Exception as ex:
                  raise Assist.BarCodeException(ex)

      @staticmethod
      def loadFileBase64String(filepath):
            with open(filepath, "r") as image_file:
                  return image_file.read().replace('\n','')

class BarcodeParameters(Assist.BaseJavaClass):
      """! Barcode generation parameters."""

      def __init__(self, javaClass):
            """!  """
            self.xDimension = None
            self.barHeight = None
            self.barCodeWidth = None
            self.barCodeHeight = None
            self.codeTextParameters = None
            self.postal = None
            self.australianPost = None
            self.codablock = None
            self.dataBar = None
            self.dataMatrix = None
            self.code16K = None
            self.itf = None
            self.qr = None
            self.pdf417 = None
            self.maxiCode = None
            self.aztec = None
            self.codabar = None
            self.coupon = None
            self.supplement = None
            self.dotCode = None
            self.padding = None
            self.patchCode = None
            self.barWidthReduction = None
            super().__init__(javaClass)


      def init(self):
            """! initialize properties """
            self.xDimension = Unit(self.getJavaClass().getXDimension())
            self.barHeight = Unit(self.getJavaClass().getBarHeight())
            self.barCodeWidth = Unit(self.getJavaClass().getBarCodeWidth())
            self.barCodeHeight = Unit(self.getJavaClass().getBarCodeHeight())
            self.codeTextParameters = CodetextParameters(self.getJavaClass().getCodeTextParameters())
            self.postal = PostalParameters(self.getJavaClass().getPostal())
            self.australianPost = AustralianPostParameters(self.getJavaClass().getAustralianPost())
            self.codablock = CodablockParameters(self.getJavaClass().getCodablock())
            self.dataBar = DataBarParameters(self.getJavaClass().getDataBar())
            self.dataMatrix = DataMatrixParameters(self.getJavaClass().getDataMatrix())
            self.code16K = Code16KParameters(self.getJavaClass().getCode16K())
            self.itf = ITFParameters(self.getJavaClass().getITF())
            self.qr = QrParameters(self.getJavaClass().getQR())
            self.pdf417 = Pdf417Parameters(self.getJavaClass().getPdf417())
            self.maxiCode = MaxiCodeParameters(self.getJavaClass().getMaxiCode())
            self.aztec = AztecParameters(self.getJavaClass().getAztec())
            self.codabar = CodabarParameters(self.getJavaClass().getCodabar())
            self.coupon = CouponParameters(self.getJavaClass().getCoupon())
            self.supplement = SupplementParameters(self.getJavaClass().getSupplement())
            self.dotCode = DotCodeParameters(self.getJavaClass().getDotCode())
            self.padding = Padding(self.getJavaClass().getPadding())
            self.patchCode = PatchCodeParameters(self.getJavaClass().getPatchCode())
            self.barWidthReduction = Unit(self.getJavaClass().getBarWidthReduction())

      def getXDimension(self):
            """!
             x-dimension is the smallest width of the unit of BarCode bars or spaces.
             Increase this will increase the whole barcode image width.
            Ignored if AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.  """
            return self.xDimension

      def setXDimension(self, value):
            """!  x-dimension is the smallest width of the unit of BarCode bars or spaces.
          Increase this will increase the whole barcode image width.
          Ignored if AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
          @throws BarCodeException """
            self.getJavaClass().setXDimension(value.getJavaClass())
            self.xDimension = value

      def getBarWidthReduction(self):
            """!  Get bars reduction value that is used to compensate ink spread while printing.
             @return Unit value of BarWidthReduction"""
            try:
                  return self.barWidthReduction
            except Exception as ex:
                  barcode_exception = Assist.BarCodeException(ex)
                  raise barcode_exception

      def setBarWidthReduction(self, value):
            """! Sets bars reduction value that is used to compensate ink spread while printing. """
            try:
                  self.getJavaClass().setBarWidthReduction(value.getJavaClass())
                  self.barWidthReduction = value
            except Exception as ex:
                  barcode_exception = Assist.BarCodeException(ex)
                  raise barcode_exception

      def getBarHeight(self):
            """!
            Height of 1D barcodes' bars in Unit value.
            Ignored if AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            @throws BarCodeException"""
            return self.barHeight

      def setBarHeight(self, value):
            """!
             Height of 1D barcodes' bars in Unit value.
             Ignored if AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            @throws BarCodeException
            """
            self.getJavaClass().setBarHeight(value.getJavaClass())
            self.barHeight = value

      def getAutoSizeMode(self):
            """!
            Specifies the different types of automatic sizing modes.
            Default value: AutoSizeMode.NONE.
            @deprecated "This method is obsolete. Call BaseGenerationParameters.getAutoSizeMode() instead."
             @throws BarCodeException
             """
            return self.getJavaClass().getAutoSizeMode()

      def setAutoSizeMode(self, value):
            """!
             Specifies the different types of automatic sizing modes.
             Default value: AutoSizeMode.NONE.
             @deprecated "This method is obsolete. Call BaseGenerationParameters.setAutoSizeMode() instead."
             @throws BarCodeException
              """
            self.getJavaClass().setAutoSizeMode(value)

      def getBarColor(self):
            """!
            Bars color, representation of an RGB tuple.
            Default value: 0
            """
            intColor = self.getJavaClass().getBarColor()
            Blue = intColor & 255
            Green = (intColor >> 8) & 255
            Red = (intColor >> 16) & 255
            rgbColor = (Red, Green, Blue)
            return rgbColor

      def setBarColor(self, value):
            """!
            Bars color, representation of an RGB tuple.
            Default value: 0.
            """
            rgb = 65536 * value[0] + 256 * value[1] + value[2]
            self.getJavaClass().setBarColor(rgb)

      def getPadding(self):
            """!
            Barcode paddings.
            Default value: 5pt 5pt 5pt 5pt.
            """
            return self.padding

      def setPadding(self, value):
            """!
            Barcode paddings.
           Default value: 5pt 5pt 5pt 5pt.
            """
            self.getJavaClass().setPadding(value.getJavaClass())
            self.padding = value

      def getChecksumAlwaysShow(self):
            """!
            Always display checksum digit in the human readable text for Code128 and GS1Code128 barcodes.
            """
            return self.getJavaClass().getChecksumAlwaysShow()

      def setChecksumAlwaysShow(self, value):
            """!
            Always display checksum digit in the human readable text for Code128 and GS1Code128 barcodes.
            """
            self.getJavaClass().setChecksumAlwaysShow(value)

      def isChecksumEnabled(self):
            """!
            Enable checksum during generation 1D barcodes.
            Default is treated as Yes for symbology which must contain checksum, as No where checksum only possible.
            Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN, Codabar
            Checksum always used: Rest symbology
            """
            return self.getJavaClass().isChecksumEnabled()

      def setChecksumEnabled(self, value):
            """!
           Enable checksum during generation 1D barcodes.
           Default is treated as Yes for symbology which must contain checksum, as No where checksum only possible.
           Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN, Codabar
           Checksum always used: Rest symbology
            """
            self.getJavaClass().setChecksumEnabled(value.value)

      def getEnableEscape(self):
            """!
            Indicates whether explains the character "\" as an escape character in CodeText property. Used for Pdf417, DataMatrix, Code128 only
            If the EnableEscape is true, "\" will be explained as a special escape character. Otherwise, "\" acts as normal characters.
           Aspose.BarCode supports inputing decimal ascii code and mnemonic for ASCII control-code characters. For example, \013 and \\CR stands for CR.
            """
            return self.getJavaClass().getEnableEscape()

      def setEnableEscape(self, value):
            """!
     Indicates whether explains the character "\" as an escape character in CodeText property. Used for Pdf417, DataMatrix, Code128 only
         If the EnableEscape is true, "\" will be explained as a special escape character. Otherwise, "\" acts as normal characters.
         <hr>Aspose.BarCode supports inputing decimal ascii code and mnemonic for ASCII control-code characters. For example, \013 and \\CR stands for CR.</hr>
            """
            self.getJavaClass().setEnableEscape(value)

      def getWideNarrowRatio(self):
            """!
         Wide bars to Narrow bars ratio.
            Default value: 3, that is, wide bars are 3 times as wide as narrow bars.
            Used for ITF, PZN, PharmaCode, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, IATA2of5, VIN, DeutschePost, OPC, Code32, DataLogic2of5, PatchCode, Code39Extended, Code39Standard
            The WideNarrowRatio parameter value is less than or equal to 0.
            """
            return self.getJavaClass().getWideNarrowRatio()

      def setWideNarrowRatio(self, value):
            """!
         Wide bars to Narrow bars ratio.
            Default value: 3, that is, wide bars are 3 times as wide as narrow bars.
            Used for ITF, PZN, PharmaCode, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, IATA2of5, VIN, DeutschePost, OPC, Code32, DataLogic2of5, PatchCode, Code39Extended, Code39Standard
            The WideNarrowRatio parameter value is less than or equal to 0.
            """
            self.getJavaClass().setWideNarrowRatio(value)

      def getCodeTextParameters(self):
            """!
         Codetext parameters.
            """
            return self.codeTextParameters

      def getFilledBars(self):
            """!
         Gets a value indicating whether bars filled.
            Only for 1D barcodes.
            Default value: true.
            """
            return self.getJavaClass().getFilledBars()

      def setFilledBars(self, value):
            """!
       Sets a value indicating whether bars filled.
           Only for 1D barcodes.
           Default value: true.
            """
            self.getJavaClass().setFilledBars(value)

      def getPostal(self):
            """!
          Postal parameters. Used for Postnet, Planet.
            """
            return self.postal

      def getPatchCode(self):
            """!
        PatchCode parameters.
            """
            return self.patchCode

      def getAustralianPost(self):
            """!
         AustralianPost barcode parameters.
            """
            return self.australianPost

      def getDataBar(self):
            """!
        Databar parameters.
            """
            return self.dataBar

      def getCodablock(self):
            """!
          Codablock parameters.
            """
            return self.codablock

      def getDataMatrix(self):
            """!
         DataMatrix parameters.
            """
            return self.dataMatrix

      def getCode16K(self):
            """!
        Code16K parameters.
            """
            return self.code16K

      def getDotCode(self):
            """!
        DotCode parameters.
            """
            return self.dotCode

      def getITF(self):
            """!
        ITF parameters.
            """
            return self.itf

      def getPdf417(self):
            """!
         PDF417 parameters.
            """
            return self.pdf417

      def getQR(self):
            """!
        QR parameters.
            """
            return self.qr

      def getSupplement(self):
            """!
          Supplement parameters. Used for Interleaved2of5, Standard2of5, EAN13, EAN8, UPCA, UPCE, ISBN, ISSN, ISMN.
            """
            return self.supplement

      def getMaxiCode(self):
            """!
         MaxiCode parameters.
            """
            return self.maxiCode

      def getAztec(self):
            """!
        Aztec parameters.
            """
            return self.aztec

      def getCodabar(self):
            """!
               Codabar parameters.
            """
            return self.codabar

      def getCoupon(self):
            """!
        Coupon parameters. Used for UpcaGs1DatabarCoupon, UpcaGs1Code128Coupon.
            """
            return self.coupon


class BaseGenerationParameters(Assist.BaseJavaClass):
      """!
      Barcode image generation parameters.
      """

      def __init__(self, javaClass):
            self.captionAbove = None
            self.captionBelow = None
            self.barcodeParameters = None
            self.borderParameters = None
            self.imageWidth = None
            self.imageHeight = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.captionAbove = CaptionParameters(self.getJavaClass().getCaptionAbove())
            self.captionBelow = CaptionParameters(self.getJavaClass().getCaptionBelow())
            self.barcodeParameters = BarcodeParameters(self.getJavaClass().getBarcode())
            self.borderParameters = BorderParameters(self.getJavaClass().getBorder())
            self.imageWidth = Unit(self.getJavaClass().getImageWidth())
            self.imageHeight = Unit(self.getJavaClass().getImageHeight())

      def getBackColor(self):
            """!
            Background color of the barcode image, representation of an RGB tuple.
            Default value: 0
            """
            intColor = self.getJavaClass().getBackColor()
            Blue = intColor & 255
            Green = (intColor >> 8) & 255
            Red = (intColor >> 16) & 255
            rgbColor = (Red, Green, Blue)
            return rgbColor

      def setBackColor(self, value):
            """!
            Background color of the barcode image, representation of an RGB tuple.
            Default value: 0
            """
            rgb = 65536 * value[0] + 256 * value[1] + value[2]
            if rgb > 16777215:
                  raise Exception("Invalid color")
            self.getJavaClass().setBackColor(rgb)

      def getResolution(self):
            """!
            Gets the resolution of the BarCode image.
            One value for both dimensions.
            Default value: 96 dpi.
            The Resolution parameter value is less than or equal to 0.
            """
            return self.getJavaClass().getResolution()

      def setResolution(self, value):
            """!
            Sets the resolution of the BarCode image.
            One value for both dimensions.
            Default value: 96 dpi.
            The Resolution parameter value is less than or equal to 0.
            """
            self.getJavaClass().setResolution(value)

      def getRotationAngle(self):
            """!
            BarCode image rotation angle, measured in degree, e.g. RotationAngle = 0 or RotationAngle = 360 means no rotation.
            If RotationAngle NOT equal to 90, 180, 270 or 0, it may increase the difficulty for the scanner to read the image.
            Default value: 0.
            This sample shows how to create and save a BarCode image.
            generator = BarcodeGenerator( EncodeTypes.DATA_MATRIX)
            generator.getParameters().setRotationAngle(7)
            generator.save("test.png")
            """
            return self.getJavaClass().getRotationAngle()

      def setRotationAngle(self, value):
            """!
            BarCode image rotation angle, measured in degree, e.g. RotationAngle = 0 or RotationAngle = 360 means no rotation.
            If RotationAngle NOT equal to 90, 180, 270 or 0, it may increase the difficulty for the scanner to read the image.
            Default value: 0.
            This sample shows how to create and save a BarCode image.
            generator = BarcodeGenerator( EncodeTypes.DATA_MATRIX)
            generator.getParameters().setRotationAngle(7)
            generator.save("test.png")
            """
            self.getJavaClass().setRotationAngle(value)

      def getCaptionAbove(self):
            """!
            Caption Above the BarCode image. See CaptionParameters.
            """
            return self.captionAbove

      def setCaptionAbove(self, value):
            """!
            Caption Above the BarCode image. See CaptionParameters.
            """
            self.getJavaClass().setCaptionAbove(value.getJavaClass())
            self.captionAbove.updateCaption(value)

      def getCaptionBelow(self):
            """!
            Caption Below the BarCode image. See CaptionParameters.
            """
            return self.captionBelow

      def setCaptionBelow(self, value):
            """!
            Caption Below the BarCode image. See CaptionParameters.
            """
            self.getJavaClass().setCaptionBelow(value.getJavaClass())
            self.captionBelow.updateCaption(value)

      def getAutoSizeMode(self):
            """!
            Specifies the different types of automatic sizing modes.
            Default value: AutoSizeMode.NONE.
            """
            return AutoSizeMode(self.getJavaClass().getAutoSizeMode())

      def setAutoSizeMode(self, value):
            """!
            Specifies the different types of automatic sizing modes.
            Default value: AutoSizeMode.NONE.
            """
            self.getJavaClass().setAutoSizeMode(str(value.value))

      def getImageHeight(self):
            """!
    BarCode image height when AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            """
            return self.imageHeight

      def setImageHeight(self, value):
            """!
    BarCode image height when AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            """
            self.getJavaClass().setImageHeight(value.getJavaClass())
            self.imageHeight = value

      def getImageWidth(self):
            """!
    BarCode image width when AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            """
            return self.imageWidth

      def setImageWidth(self, value):
            """!
    BarCode image width when AutoSizeMode property is set to AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            """
            self.getJavaClass().setImageWidth(value.getJavaClass())
            self.imageWidth = value

      def getBarcode(self):
            """!
    Gets the BarcodeParameters that contains all barcode properties.
            """
            return self.barcodeParameters

      def setBarcode(self, value):
            """!
    Gets the BarcodeParameters that contains all barcode properties.
            """
            self.getJavaClass().setBarcode(value.getJavaClass())
            self.barcodeParameters = value

      def getBorder(self):
            """!
    Gets the BorderParameters that contains all configuration properties for barcode border.
            """
            return self.borderParameters


class BorderParameters(Assist.BaseJavaClass):
      """!
      Barcode image border parameters
      """

      def __init__(self, javaClass):
            self.width = None
            super().__init__(javaClass)

      def init(self):
            self.width = Unit(self.getJavaClass().getWidth())

      def getVisible(self):
            """!
          Border visibility. If false than parameter Width is always ignored (0).
            Default value: false.
            """
            return self.getJavaClass().getVisible()

      def setVisible(self, value):
            """!
        Border visibility. If false than parameter Width is always ignored (0).
            Default value: false.
            """
            self.getJavaClass().setVisible(value)

      def getWidth(self):
            """!
         Border width.
            Default value: 0.
            Ignored if Visible is set to false.
            """
            return self.width

      def setWidth(self, value):
            """!
           Border width.
            Default value: 0.
            Ignored if Visible is set to false.
            """
            self.getJavaClass().setWidth(value.getJavaClass())
            self.width = value

      def toString(self):
            """!
          Returns a human-readable string representation of this BorderParameters.
            @return A string that represents this BorderParameters.
            """
            return self.getJavaClass().toString()

      def getDashStyle(self):
            """!
         Border dash style.
            Default value: BorderDashStyle.SOLID.
            """
            return BorderDashStyle(self.getJavaClass().getDashStyle())

      def setDashStyle(self, value):
            """!
        Border dash style.
            Default value: BorderDashStyle.SOLID.
            """
            self.getJavaClass().setDashStyle(value.value)

      def getColor(self):
            """!
        Border color, representation of an RGB tuple.
            Default value: 0
            """
            intColor = self.getJavaClass().getColor()
            Blue = intColor & 255
            Green = (intColor >> 8) & 255
            Red = (intColor >> 16) & 255
            rgbColor = (Red, Green, Blue)
            return rgbColor

      def setColor(self, value):
            """!
         Border color, representation of an RGB tuple.
            Default value: 0
            """
            rgb = 65536 * value[0] + 256 * value[1] + value[2]
            self.getJavaClass().setColor(rgb)


class CaptionParameters(Assist.BaseJavaClass):
      """!
      Caption parameters.
      """

      def __init__(self, javaClass):
            self.font = None
            self.padding = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.padding = Padding(self.getJavaClass().getPadding())
            self.font = FontUnit(self.getJavaClass().getFont())

      def getText(self):
            """!
         Caption text.
            Default value: empty string.
            """
            return self.getJavaClass().getText()

      def setText(self, value):
            """!
        Caption text.
            Default value: empty string.
            """
            self.getJavaClass().setText(value)

      def getFont(self):
            """!
          Caption font.
            Default value: Arial 8pt regular.
            """
            return self.font

      def getVisible(self):
            """!
         Caption text visibility.
            Default value: false.
            """
            return self.getJavaClass().getVisible()

      def setVisible(self, value):
            """!
         Caption text visibility.
            Default value: false.
            """
            self.getJavaClass().setVisible(value)

      def getTextColor(self):
            """!
            Caption text color, representation of an RGB tuple.
            Default value (0,0,0).
            """
            intColor = self.getJavaClass().getTextColor()
            Blue = intColor & 255
            Green = (intColor >> 8) & 255
            Red = (intColor >> 16) & 255
            rgbColor = (Red, Green, Blue)
            return rgbColor

      def setTextColor(self, value):
            """!
           Caption text color, representation of an RGB tuple.
            Default value (0,0,0).
            """
            rgb = 65536 * value[0] + 256 * value[1] + value[2]
            self.getJavaClass().setTextColor(rgb)

      def getPadding(self):
            """!
        Captions paddings.
            Default value for CaptionAbove: 5pt 5pt 0 5pt.
            Default value for CaptionBelow: 0 5pt 5pt 5pt.
            """
            return self.padding

      def setPadding(self, value):
            """!
          Captions paddings.
            Default value for CaptionAbove: 5pt 5pt 0 5pt.
            Default value for CaptionBelow: 0 5pt 5pt 5pt.
            """
            self.getJavaClass().setPadding(value.getJavaClass())
            self.padding = value

      def getAlignment(self):
            """!
          Caption test horizontal alignment.
            Default valueAlignment.Center.
            """
            return TextAlignment(self.getJavaClass().getAlignment())

      def setAlignment(self, value):
            """!
         Caption test horizontal alignment.
            Default valueAlignment.Center.
            """
            self.getJavaClass().setAlignment(value.value)

      def getNoWrap(self):
            """!
         Specify word wraps (line breaks) within text.
            @return bool
            """
            return self.getJavaClass().getNoWrap()

      def setNoWrap(self, value):
            """!
          Specify word wraps (line breaks) within text.
            """
            self.getJavaClass().setNoWrap(value)


class Unit(Assist.BaseJavaClass):
      """!
        Specifies the size value in different units (Pixel, Inches, etc.).

        This sample shows how to create and save a BarCode image.
        \code
              generator = BarcodeGenerator(EncodeTypes.CODE_128)
              generator.getParameters().getBarcode().getBarHeight().setMillimeters(10)
              generator.save("test.png")
        \endcode
      """

      def __init__(self, source):
            super().__init__(Unit.initUnit(source))
            self.init()

      @staticmethod
      def initUnit(source):
            if isinstance(source, Unit):
                  return source.getNativeObject()
            return source

      def init(self):
            pass

      def getPixels(self):
            """!
          Gets size value in pixels.
            """
            return self.getJavaClass().getPixels()

      def setPixels(self, value):
            """!
        Sets size value in pixels.
            """
            self.getJavaClass().setPixels(value)

      def getInches(self):
            """!
         Gets size value in inches.
            """
            return self.getJavaClass().getInches()

      def setInches(self, value):
            """!
           Sets size value in inches.
            """
            self.getJavaClass().setInches(value)

      def getMillimeters(self):
            """!
         Gets size value in millimeters.
            """
            return self.getJavaClass().getMillimeters()

      def setMillimeters(self, value):
            """!
        Sets size value in millimeters.
            """
            self.getJavaClass().setMillimeters(value)

      def getPoint(self):
            """!
        Gets size value in point.
            """
            return self.getJavaClass().getPoint()

      def setPoint(self, value):
            """!
         Sets size value in point.
            """
            self.getJavaClass().setPoint(value)

      def getDocument(self):
            """!
        Gets size value in document units.
            """
            return self.getJavaClass().getDocument()

      def setDocument(self, value):
            """!
         Sets size value in document units.
            """
            self.getJavaClass().setDocument(value)

      def toString(self):
            """!
         Returns a human-readable string representation of this Unit.
            @return A string that represents this Unit.
            """
            return self.getJavaClass().toString()

      def equals(self, obj):
            """!
         Determines whether this instance and a specified object,
            which must also be a Unit object, have the same value.
            @param obj The Unit to compare to this instance.
            @return true if obj is a Unit and its value is the same as this instance
            otherwise, false. If obj is null, the method returns false.
            """
            return self.getJavaClass().equals(obj.getJavaClass())


class Padding(Assist.BaseJavaClass):
      """!
      Paddings parameters.
      """

      def __init__(self, javaClass):
            self.top = None
            self.bottom = None
            self.right = None
            self.left = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.top = Unit(self.getJavaClass().getTop())
            self.bottom = Unit(self.getJavaClass().getBottom())
            self.right = Unit(self.getJavaClass().getRight())
            self.left = Unit(self.getJavaClass().getLeft())

      def getTop(self):
            """!
         Top padding.
            """
            return self.top

      def setTop(self, value):
            """!
        Top padding.
            """
            self.getJavaClass().setTop(value.getJavaClass())
            self.top = value

      def getBottom(self):
            """!
          Bottom padding.
            """
            return self.bottom

      def setBottom(self, value):
            """!
         Bottom padding.
            """
            self.getJavaClass().setBottom(value.getJavaClass())
            self.bottom = value

      def getRight(self):
            """!
          Right padding.
            """
            return self.right

      def setRight(self, value):
            """!
            Right padding.
            """
            self.getJavaClass().setRight(value.getJavaClass())
            self.right = value

      def getLeft(self):
            """!
          Left padding.
            """
            return self.left

      def setLeft(self, value):
            """!
        Left padding.
            """
            self.getJavaClass().setLeft(value.getJavaClass())
            self.left = value

      def toString(self):
            """!
         Returns a human-readable string representation of this Padding.
            @return A string that represents this Padding.
            """
            return self.getJavaClass().toString()


class CodetextParameters(Assist.BaseJavaClass):
      """!
      Codetext parameters.
      """

      def __init__(self, javaClass):
            self.font = None
            self.space = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.font = FontUnit(self.getJavaClass().getFont())
            self.space = Unit(self.getJavaClass().getSpace())

      def getTwoDDisplayText(self):
            """!
         Text that will be displayed instead of codetext in 2D barcodes.
            Used for: Aztec, Pdf417, DataMatrix, QR, MaxiCode, DotCode
            """
            return self.getJavaClass().getTwoDDisplayText()

      def setTwoDDisplayText(self, value):
            """!
         Text that will be displayed instead of codetext in 2D barcodes.
            Used for: Aztec, Pdf417, DataMatrix, QR, MaxiCode, DotCode
            """
            self.getJavaClass().setTwoDDisplayText(value)

      def getFontMode(self):
            """!
          Specify FontMode. If FontMode is set to Auto, font size will be calculated automatically based on xDimension value.
            It is recommended to use FontMode.AUTO especially in AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            Default value: FontMode.AUTO.
            """
            return FontMode(int(self.getJavaClass().getFontMode()))

      def setFontMode(self, value):
            """!
           Specify FontMode. If FontMode is set to Auto, font size will be calculated automatically based on xDimension value.
            It is recommended to use FontMode.AUTO especially in AutoSizeMode.NEAREST or AutoSizeMode.INTERPOLATION.
            Default value: FontMode.AUTO.
            """
            self.getJavaClass().setFontMode(value.value)

      def getFont(self):
            """!
         Specify the displaying CodeText's font.
            Default value: Arial 5pt regular.
            Ignored if FontMode is set to FontMode.AUTO.
            """
            return self.font

      def setFont(self, value):
            """!
          Specify the displaying CodeText's font.
            Default value: Arial 5pt regular.
            Ignored if FontMode is set to FontMode.AUTO.
            """
            self.getJavaClass().setFont(value.getJavaClass())
            self.font = value

      def getSpace(self):
            """!
         Space between the CodeText and the BarCode in Unit value.
            Default value: 2pt.
            Ignored for EAN8, EAN13, UPCE, UPCA, ISBN, ISMN, ISSN, UpcaGs1DatabarCoupon.
            """
            return self.space

      def setSpace(self, value):
            """!
         Space between the CodeText and the BarCode in Unit value.
            Default value: 2pt.
            Ignored for EAN8, EAN13, UPCE, UPCA, ISBN, ISMN, ISSN, UpcaGs1DatabarCoupon.
            """
            self.getJavaClass().setSpace(value.getJavaClass())
            self.space = value

      def getAlignment(self):
            """!
          Gets or sets the alignment of the code text.
            Default value: TextAlignment.CENTER.
            """
            return TextAlignment(self.getJavaClass().getAlignment())

      def setAlignment(self, value):
            """!
         Gets or sets the alignment of the code text.
            Default value: TextAlignment.CENTER.
            """
            self.getJavaClass().setAlignment(value.value)

      def getColor(self):
            """!
        Specify the displaying CodeText's Color, representation of an RGB tuple.
            Default value (0,0,0).
            """
            intColor = self.getJavaClass().getColor()
            Blue = intColor & 255
            Green = (intColor >> 8) & 255
            Red = (intColor >> 16) & 255
            rgbColor = (Red, Green, Blue)
            return rgbColor

      def setColor(self, value):
            """!
        Specify the displaying CodeText's Color, representation of an RGB tuple.
            Default value (0,0,0).
            """
            rgb = 65536 * value[0] + 256 * value[1] + value[2]
            self.getJavaClass().setColor(rgb)

      def getLocation(self):
            """!
         Specify the displaying CodeText Location, set to CodeLocation.NONE to hide CodeText.
            Default value:  CodeLocation.BELOW.
            """
            return CodeLocation(self.getJavaClass().getLocation())

      def setLocation(self, value):
            """!
         Specify the displaying CodeText Location, set to  CodeLocation.NONE to hide CodeText.
            Default value:  CodeLocation.BELOW.
            """
            self.getJavaClass().setLocation(value.value)

      def getNoWrap(self):
            """!
                Specify word wraps (line breaks) within text.
            @return bool
            """
            return self.getJavaClass().getNoWrap()

      def setNoWrap(self, value):
            """!
                Specify word wraps (line breaks) within text.
            """
            self.getJavaClass().setNoWrap(value)

      def toString(self):
            """!
                Returns a human-readable string representation of this CodetextParameters.
            @return A string that represents this CodetextParameters.
            """
            return self.getJavaClass().toString()


class PostalParameters(Assist.BaseJavaClass):
      """!
      Postal parameters. Used for Postnet, Planet.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.postalShortBarHeight = None
            self.init()

      def init(self):
            self.postalShortBarHeight = Unit(self.getJavaClass().getPostalShortBarHeight())

      def getPostalShortBarHeight(self):
            """!
          Short bar's height of Postal barcodes.
            """
            return self.postalShortBarHeight

      def setPostalShortBarHeight(self, value):
            """!
        Short bar's height of Postal barcodes.
            """
            self.getJavaClass().setPostalShortBarHeight(value.getJavaClass())
            self.postalShortBarHeight = value

      def toString(self):
            """!
        Returns a human-readable string representation of this PostalParameters.
            @return A string that represents this PostalParameters.
            """
            return self.getJavaClass().toString()


class AustralianPostParameters(Assist.BaseJavaClass):
      """!
      AustralianPost barcode parameters.
      """

      def __init__(self, javaClass):
            self.australianPostShortBarHeight = None
            super().__init__(javaClass)

      def init(self):
            self.australianPostShortBarHeight = Unit(self.getJavaClass().getAustralianPostShortBarHeight())

      def getAustralianPostShortBarHeight(self):
            """!
        Short bar's height of AustralianPost barcode.
            """
            return self.australianPostShortBarHeight

      def setAustralianPostShortBarHeight(self, value):
            """!
        Short bar's height of AustralianPost barcode.
            """
            self.getJavaClass().setAustralianPostShortBarHeight(value.getJavaClass())
            self.australianPostShortBarHeight = value

      def getAustralianPostEncodingTable(self):
            """!
            Interpreting type for the Customer Information of AustralianPost, default to CustomerInformationInterpretingType.Other
            """
            return CustomerInformationInterpretingType(self.getJavaClass().getAustralianPostEncodingTable())

      def setAustralianPostEncodingTable(self, value):
            """!
            Interpreting type for the Customer Information of AustralianPost, default to CustomerInformationInterpretingType.Other"
            """
            self.getJavaClass().setAustralianPostEncodingTable(value.value)

      def toString(self):
            """!
           Returns a human-readable string representation of this AustralianPostParameters.
            @return A string that represents this AustralianPostParameters.
            """
            return self.getJavaClass().toString()


class CodablockParameters(Assist.BaseJavaClass):
      """!
      Codablock parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getColumns(self):
            """!
          Columns count.
            """
            return self.getJavaClass().getColumns()

      def setColumns(self, value):
            """!
        Columns count.
            """
            self.getJavaClass().setColumns(value)

      def getRows(self):
            """!
        Rows count.
            """
            return self.getJavaClass().getRows()

      def setRows(self, value):
            """!
        Rows count.
            """
            self.getJavaClass().setRows(value)

      def getAspectRatio(self):
            """!
         Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
          Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this CodablockParameters.
            @return A string that represents this CodablockParameters.
            """
            return self.getJavaClass().toString()


class DataBarParameters(Assist.BaseJavaClass):
      """!
      Databar parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def is2DCompositeComponent(self):
            """!
         Enables flag of 2D composite component with DataBar barcode
            """
            return self.getJavaClass().is2DCompositeComponent()

      def set2DCompositeComponent(self, value):
            """!
           Enables flag of 2D composite component with DataBar barcode
            """
            self.getJavaClass().set2DCompositeComponent(value)

      def isAllowOnlyGS1Encoding(self):
            """!
         If this flag is set, it allows only GS1 encoding standard for Databar barcode types
            """
            return self.getJavaClass().isAllowOnlyGS1Encoding()

      def setAllowOnlyGS1Encoding(self, value):
            """!
        If this flag is set, it allows only GS1 encoding standard for Databar barcode types
            """
            self.getJavaClass().setAllowOnlyGS1Encoding(value)

      def getColumns(self):
            """!
         Columns count.
            """
            return self.getJavaClass().getColumns()

      def setColumns(self, value):
            """!
        Columns count.
            """
            self.getJavaClass().setColumns(value)

      def getRows(self):
            """!
        Rows count.
            """
            return self.getJavaClass().getRows()

      def setRows(self, value):
            """!
        Rows count.
            """
            self.getJavaClass().setRows(value)

      def getAspectRatio(self):
            """!
        Height/Width ratio of 2D BarCode module.
            Used for DataBar stacked.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            Used for DataBar stacked.
            """
            self.getJavaClass().setAspectRatio(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this DataBarParameters.
            @return A string that represents this DataBarParameters.
            """
            return self.getJavaClass().toString()


class DataMatrixParameters(Assist.BaseJavaClass):
      """!
      DataMatrix parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getDataMatrixEcc(self):
            """!
         Gets a Datamatrix ECC type.
            Default value: DataMatrixEccType.ECC_200.
            """
            return DataMatrixEccType(self.getJavaClass().getDataMatrixEcc())

      def setDataMatrixEcc(self, value):
            """!
         Sets a Datamatrix ECC type.
            Default value: DataMatrixEccType.ECC_200.
            """
            self.getJavaClass().setDataMatrixEcc(value.value)

      def getDataMatrixEncodeMode(self):
            """!
           Encode mode of Datamatrix barcode.
            Default value: DataMatrixEncodeMode.AUTO.
            """
            return DataMatrixEncodeMode(self.getJavaClass().getDataMatrixEncodeMode())

      def setDataMatrixEncodeMode(self, value):
            """!
         Encode mode of Datamatrix barcode.
            Default value: DataMatrixEncodeMode.AUTO.
            """
            self.getJavaClass().setDataMatrixEncodeMode(value.value)

      def getMacroCharacters(self):
            """!
         ISO/IEC 16022
            5.2.4.7 Macro characters
            11.3 Protocol for Macro characters in the first position (ECC 200 only)
            Macro Characters 05 and 06 values are used to obtain more compact encoding in special modes.
            Can be used only with DataMatrixEccType.Ecc200 or DataMatrixEccType.EccAuto.
            Cannot be used with EncodeTypes.GS_1_DATA_MATRIX
            Default value: MacroCharacter.NONE.
            """
            return self.getJavaClass().getMacroCharacters()

      def setMacroCharacters(self, value):
            """!
          ISO/IEC 16022
             5.2.4.7 Macro characters
             11.3 Protocol for Macro characters in the first position (ECC 200 only)
             Macro Characters 05 and 06 values are used to obtain more compact encoding in special modes.
             Can be used only with DataMatrixEccType.Ecc200 or DataMatrixEccType.EccAuto.
             Cannot be used with EncodeTypes.GS_1_DATA_MATRIX
             Default value: MacroCharacter.NONE.
            """
            self.getJavaClass().setMacroCharacters(value)

      def getColumns(self):
            """!
         Columns count.
            """
            return self.getJavaClass().getColumns()

      def setColumns(self, value):
            """!
           Columns count.
            """
            self.getJavaClass().setColumns(value)

      def getRows(self):
            """!
        Rows count.
            """
            return self.getJavaClass().getRows()

      def setRows(self, value):
            """!
         Rows count.
            """
            self.getJavaClass().setRows(value)

      def getAspectRatio(self):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def getCodeTextEncoding(self):
            """!
        Gets the encoding of codetext.
            Default value: UTF-16
            """
            return self.getJavaClass().getCodeTextEncoding().toString()

      def setCodeTextEncoding(self, value):
            """!
         Sets the encoding of codetext.
            Default value: UTF-16
            """
            self.getJavaClass().setCodeTextEncoding(value)

      def toString(self):
            """!
         Returns a human-readable string representation of this DataMatrixParameters.
            @return presentation of this DataMatrixParameters.
            """
            return self.getJavaClass().toString()


class PatchCodeParameters(Assist.BaseJavaClass):
      """!
      PatchCode parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getExtraBarcodeText(self):
            """!
        Specifies codetext for an extra QR barcode, when PatchCode is generated in page mode.
            """
            return self.getJavaClass().getExtraBarcodeText()

      def setExtraBarcodeText(self, value):
            """!
        Specifies codetext for an extra QR barcode, when PatchCode is generated in page mode.
            """
            self.getJavaClass().setExtraBarcodeText(value)

      def getPatchFormat(self):
            """!
        PatchCode format. Choose PatchOnly to generate single PatchCode. Use page format to generate Patch page with PatchCodes as borders.
            Default value: PatchFormat.PATCH_ONLY
            @return PatchFormat
            """
            return PatchFormat(self.getJavaClass().getPatchFormat())

      def setPatchFormat(self, value):
            """!
        PatchCode format. Choose PatchOnly to generate single PatchCode. Use page format to generate Patch page with PatchCodes as borders.
            Default value: PatchFormat.PATCH_ONLY
            """
            self.getJavaClass().setPatchFormat(int(value.value))

      def toString(self):
            """!
        Returns a human-readable string representation of this <see cref="PatchCodeParameters"/>.
            @return A string that represents this <see cref="PatchCodeParameters"/>.
            """
            return self.getJavaClass().toString()


class Code16KParameters(Assist.BaseJavaClass):
      """!
      Code16K parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getAspectRatio(self):
            """!
         Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def getQuietZoneLeftCoef(self):
            """!
         Size of the left quiet zone in xDimension.
            Default value: 10, meaning if xDimension = 2px than left quiet zone will be 20px.
            """
            return self.getJavaClass().getQuietZoneLeftCoef()

      def setQuietZoneLeftCoef(self, value):
            """!
         Size of the left quiet zone in xDimension.
            Default value: 10, meaning if xDimension = 2px than left quiet zone will be 20px.
            """
            self.getJavaClass().setQuietZoneLeftCoef(value)

      def getQuietZoneRightCoef(self):
            """!
         Size of the right quiet zone in xDimension.
            Default value: 1, meaning if xDimension = 2px than right quiet zone will be 2px.
            """
            return self.getJavaClass().getQuietZoneRightCoef()

      def setQuietZoneRightCoef(self, value):
            """!
        Size of the right quiet zone in xDimension.
            Default value: 1, meaning if xDimension = 2px than right quiet zone will be 2px.
            """
            self.getJavaClass().setQuietZoneRightCoef(value)

      def toString(self):
            """!
          Returns a human-readable string representation of this Code16KParameters.
            @return A string that represents this Code16KParameters.
            """
            return self.getJavaClass().toString()


class DotCodeParameters(Assist.BaseJavaClass):
      """!
      DotCode parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getDotCodeMask(self):
            """!
          Mask of Dotcode barcode.
            Default value: -1.
            """
            return self.getJavaClass().getDotCodeMask()

      def setDotCodeMask(self, value):
            """!
          Mask of Dotcode barcode.
            Default value: -1.
            """
            self.getJavaClass().setDotCodeMask(value)

      def getAspectRatio(self):
            """!
         Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this DotCodeParameters.
            @return A string that represents this DotCodeParameters.
            """
            return self.getJavaClass().toString()


class ITFParameters(Assist.BaseJavaClass):
      """!
      ITF parameters.
      """

      def __init__(self, javaClass):
            self.itfBorderThickness = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.itfBorderThickness = Unit(self.getJavaClass().getItfBorderThickness())

      def getItfBorderThickness(self):
            """!
        Gets or sets an ITF border (bearer bar) thickness in Unit value.
            Default value: 12pt.
            """
            return self.itfBorderThickness

      def setItfBorderThickness(self, value):
            """!
         Gets or sets an ITF border (bearer bar) thickness in Unit value.
            Default value: 12pt.
            """
            self.getJavaClass().setItfBorderThickness(value.getJavaClass())
            self.itfBorderThickness = value

      def getItfBorderType(self):
            """!
         Border type of ITF barcode.
            Default value: ITF14BorderType.BAR.
            """
            return ITF14BorderType(int(self.getJavaClass().getItfBorderType()))

      def setItfBorderType(self, value):
            """!
        Border type of ITF barcode.
            Default value: ITF14BorderType.BAR.
            """
            self.getJavaClass().setItfBorderType(value.value)

      def getQuietZoneCoef(self):
            """!
        Size of the quiet zones in xDimension.
            Default value: 10, meaning if xDimension = 2px than quiet zones will be 20px.
            @exception IllegalArgumentException
            The QuietZoneCoef parameter value is less than 10.
            """
            return self.getJavaClass().getQuietZoneCoef()

      def setQuietZoneCoef(self, value):
            """!
          Size of the quiet zones in xDimension.
            Default value: 10, meaning if xDimension = 2px than quiet zones will be 20px.
            @exception IllegalArgumentException
            The QuietZoneCoef parameter value is less than 10.
            """
            self.getJavaClass().setQuietZoneCoef(value)

      def toString(self):
            """!
         Returns a human-readable string representation of this ITFParameters.
            @return A string that represents this ITFParameters.
            """
            return self.getJavaClass().toString()


class QrParameters(Assist.BaseJavaClass):
      """!
      QR parameters.
      """

      def __init__(self, javaClass):
            self.structuredAppend = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self.structuredAppend = QrStructuredAppendParameters(self.getJavaClass().getStructuredAppend())

      def getStructuredAppend(self):
            """!
        QR structured append parameters.
            """
            return self.structuredAppend

      def setStructuredAppend(self, value):
            """!
        QR structured append parameters.
            """
            self.structuredAppend = value
            self.getJavaClass().setStructuredAppend(value.getJavaClass())

      def getQrECIEncoding(self):
            """!
        Extended Channel Interpretation Identifiers. It is used to tell the barcode reader details
            about the used references for encoding the data in the symbol.
            Current implementation consists all well known charset encodings.
            """
            return ECIEncodings(self.getJavaClass().getQrECIEncoding())

      def setQrECIEncoding(self, value):
            """!
        Extended Channel Interpretation Identifiers. It is used to tell the barcode reader details
            about the used references for encoding the data in the symbol.
            Current implementation consists all well known charset encodings.
            """
            self.getJavaClass().setQrECIEncoding(value.value)

      def getQrEncodeMode(self):
            """!
        QR symbology type of BarCode's encoding mode.
            Default value: QREncodeMode.AUTO.
            """
            return QREncodeMode(int(self.getJavaClass().getQrEncodeMode()))

      def setQrEncodeMode(self, value):
            """!
         QR symbology type of BarCode's encoding mode.
            Default value: QREncodeMode.AUTO.
            """
            self.getJavaClass().setQrEncodeMode(value.value)

      def getQrEncodeType(self):
            """!
        QR / MicroQR selector mode. Select ForceQR for standard QR symbols, Auto for MicroQR.
            """
            return QREncodeType(int(self.getJavaClass().getQrEncodeType()))

      def setQrEncodeType(self, value):
            """!
         QR / MicroQR selector mode. Select ForceQR for standard QR symbols, Auto for MicroQR.
            """
            self.getJavaClass().setQrEncodeType(value.value)

      def getQrErrorLevel(self):
            """!
           Level of Reed-Solomon error correction for QR barcode.
             From low to high: LEVEL_L, LEVEL_M, LEVEL_Q, LEVEL_H. see QRErrorLevel.
            """
            return QRErrorLevel(int(self.getJavaClass().getQrErrorLevel()))

      def setQrErrorLevel(self, value):
            """!
         Level of Reed-Solomon error correction for QR barcode.
             From low to high: LEVEL_L, LEVEL_M, LEVEL_Q, LEVEL_H. see QRErrorLevel.
            """
            self.getJavaClass().setQrErrorLevel(value.value)

      def getQrVersion(self):
            """!
        Version of QR Code.
            From Version1 to Version40 for QR code and from M1 to M4 for MicroQr.
            Default value is QRVersion.AUTO.
            """
            return QRVersion(int(self.getJavaClass().getQrVersion()))

      def setQrVersion(self, value):
            """!
        Version of QR Code.
            From Version1 to Version40 for QR code and from M1 to M4 for MicroQr.
            Default value is QRVersion.AUTO.
            """
            self.getJavaClass().setQrVersion(value.value)

      def getAspectRatio(self):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
         Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def getCodeTextEncoding(self):
            """!
         Gets the encoding of codetext.
            Default value: UTF-8
            """
            return self.getJavaClass().getCodeTextEncoding()

      def setCodeTextEncoding(self, value):
            """!
          Sets the encoding of codetext.
            Default value: UTF-8
            """
            self.getJavaClass().setCodeTextEncoding(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this QrParameters.
            @return A string that represents this QrParameters.
            """
            return self.getJavaClass().toString()


class Pdf417Parameters(Assist.BaseJavaClass):
      """!
      PDF417 parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getPdf417CompactionMode(self):
            """!
         Pdf417 symbology type of BarCode's compaction mode.
            Default value: Pdf417CompactionMode.AUTO.
            """
            return Pdf417CompactionMode(self.getJavaClass().getPdf417CompactionMode())

      def setPdf417CompactionMode(self, value):
            """!
         Pdf417 symbology type of BarCode's compaction mode.
            Default value: Pdf417CompactionMode.AUTO.
            """
            self.getJavaClass().setPdf417CompactionMode(value.value)

      def getPdf417ErrorLevel(self):
            """!
        Gets or sets Pdf417 symbology type of BarCode's error correction level
            ranging from level0 to level8, level0 means no error correction info,
            level8 means best error correction which means a larger picture.
            """
            return Pdf417ErrorLevel(self.getJavaClass().getPdf417ErrorLevel())

      def setPdf417ErrorLevel(self, value):
            """!
        Gets or sets Pdf417 symbology type of BarCode's error correction level
            ranging from level0 to level8, level0 means no error correction info,
            level8 means best error correction which means a larger picture.
            """
            self.getJavaClass().setPdf417ErrorLevel(value.value)

      def getPdf417Truncate(self):
            """!
        Whether Pdf417 symbology type of BarCode is truncated (to reduce space).
            """
            return self.getJavaClass().getPdf417Truncate()

      def setPdf417Truncate(self, value):
            """!
         Whether Pdf417 symbology type of BarCode is truncated (to reduce space).
            """
            self.getJavaClass().setPdf417Truncate(value)

      def getColumns(self):
            """!
                 Columns count.
            """
            return int(self.getJavaClass().getColumns())

      def setColumns(self, value):
            """!
         Columns count.
            """
            self.getJavaClass().setColumns(value)

      def getRows(self):
            """!
         Rows count.
            """
            return int(self.getJavaClass().getRows())

      def setRows(self, value):
            """!
        Rows count.
            """
            self.getJavaClass().setRows(value)

      def getAspectRatio(self):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def getPdf417MacroFileID(self):
            """!
         Getsmacro Pdf417 barcode's file ID.
            Used for MacroPdf417.
            """
            return self.getJavaClass().getPdf417MacroFileID()

      def setPdf417MacroFileID(self, value):
            """!
         Sets macro Pdf417 barcode's file ID.
            Used for MacroPdf417.
            """
            self.getJavaClass().setPdf417MacroFileID(value)

      def getPdf417MacroSegmentID(self):
            """!
        Gets macro Pdf417 barcode's segment ID, which starts from 0, to MacroSegmentsCount - 1.
            """
            return self.getJavaClass().getPdf417MacroSegmentID()

      def setPdf417MacroSegmentID(self, value):
            """!
          Sets macro Pdf417 barcode's segment ID, which starts from 0, to MacroSegmentsCount - 1.
            """
            self.getJavaClass().setPdf417MacroSegmentID(value)

      def getPdf417MacroSegmentsCount(self):
            """!
        Gets macro Pdf417 barcode segments count.
            """
            return self.getJavaClass().getPdf417MacroSegmentsCount()

      def setPdf417MacroSegmentsCount(self, value):
            """!
        Sets macro Pdf417 barcode segments count.
            """
            self.getJavaClass().setPdf417MacroSegmentsCount(value)

      def getPdf417MacroFileName(self):
            """!
        Gets macro Pdf417 barcode file name.
            """
            return self.getJavaClass().getPdf417MacroFileName()

      def setPdf417MacroFileName(self, value):
            """!
                 Sets macro Pdf417 barcode file name.
            """
            self.getJavaClass().setPdf417MacroFileName(value)

      def getPdf417MacroTimeStamp(self):
            """!
        Gets macro Pdf417 barcode time stamp.
            """
            return datetime.fromtimestamp(int(str(self.getJavaClass().getPdf417MacroTimeStamp())))

      def setPdf417MacroTimeStamp(self, value):
            """!
        Sets macro Pdf417 barcode time stamp.
            """
            self.getJavaClass().setPdf417MacroTimeStamp(str(int(time.mktime(value.timetuple()))))

      def getPdf417MacroSender(self):
            """!
         Gets macro Pdf417 barcode sender name.
            """
            return self.getJavaClass().getPdf417MacroSender()

      def setPdf417MacroSender(self, value):
            """!
          Sets macro Pdf417 barcode sender name.
            """
            self.getJavaClass().setPdf417MacroSender(value)

      def getPdf417MacroAddressee(self):
            """!
        Gets macro Pdf417 barcode addressee name.
            """
            return self.getJavaClass().getPdf417MacroAddressee()

      def setPdf417MacroAddressee(self, value):
            """!
         Sets macro Pdf417 barcode addressee name.
            """
            self.getJavaClass().setPdf417MacroAddressee(value)

      def getPdf417MacroFileSize(self):
            """!
         Gets or sets macro Pdf417 file size.
            @return The file size field contains the size in bytes of the entire source file.
            """
            return self.getJavaClass().getPdf417MacroFileSize()

      def setPdf417MacroFileSize(self, value):
            """!
         Gets or sets macro Pdf417 file size.
            @param value The file size field contains the size in bytes of the entire source file.
            """
            self.getJavaClass().setPdf417MacroFileSize(value)

      def getPdf417MacroChecksum(self):
            """!
         Gets macro Pdf417 barcode checksum.
            @return The checksum field contains the value of the 16-bit (2 bytes) CRC checksum using the CCITT-16 polynomial.
            """
            return self.getJavaClass().getPdf417MacroChecksum()

      def setPdf417MacroChecksum(self, value):
            """!
          Sets macro Pdf417 barcode checksum.
            @param value The checksum field contains the value of the 16-bit (2 bytes) CRC checksum using the CCITT-16 polynomial.
            """
            self.getJavaClass().setPdf417MacroChecksum(value)

      def getCodeTextEncoding(self):
            """!
           Gets the encoding of codetext.
            Default value: UTF-8
            """
            return self.getJavaClass().getCodeTextEncoding()

      def setCodeTextEncoding(self, value):
            """!
            Sets the encoding of codetext.
            Default value: UTF-8
            """
            self.getJavaClass().setCodeTextEncoding(value)

      def getPdf417ECIEncoding(self):
            """!
         Extended Channel Interpretation Identifiers. It is used to tell the barcode reader details
            about the used references for encoding the data in the symbol.
            Current implementation consists all well known charset encodings.
            """
            return ECIEncodings(self.getJavaClass().getPdf417ECIEncoding())

      def setPdf417ECIEncoding(self, value):
            """!
        Extended Channel Interpretation Identifiers. It is used to tell the barcode reader details
            about the used references for encoding the data in the symbol.
            Current implementation consists all well known charset encodings.
            """
            self.getJavaClass().setPdf417ECIEncoding(value.value)

      def getPdf417MacroECIEncoding(self):
            """!
        Extended Channel Interpretation Identifiers. Applies for Macro PDF417 text fields.
            """
            return self.getJavaClass().getPdf417MacroECIEncoding()

      def setPdf417MacroECIEncoding(self, value):
            """!
        Extended Channel Interpretation Identifiers. Applies for Macro PDF417 text fields.
            """
            self.getJavaClass().setPdf417MacroECIEncoding(value)

      def isReaderInitialization(self):
            """!
          Used to instruct the reader to interpret the data contained within the symbol
            as programming for reader initialization
            @return
            """
            return self.getJavaClass().isReaderInitialization()

      def setReaderInitialization(self, value):
            """!
         Used to instruct the reader to interpret the data contained within the symbol
            as programming for reader initialization
            @param value
            """
            self.getJavaClass().setReaderInitialization(value)

      def getCode128Emulation(self):
            """!
         Function codeword for Code 128 emulation. Applied for MicroPDF417 only.  Ignored for PDF417 and MacroPDF417 barcodes.
            """
            return self.getJavaClass().getCode128Emulation()

      def setCode128Emulation(self, value):
            """!
          Function codeword for Code 128 emulation. Applied for MicroPDF417 only.  Ignored for PDF417 and MacroPDF417 barcodes.
            """
            self.getJavaClass().setCode128Emulation(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this Pdf417Parameters.
            @return A string that represents this Pdf417Parameters.
            """
            return self.getJavaClass().toString()


class SupplementParameters(Assist.BaseJavaClass):
      """!
      Supplement parameters. Used for Interleaved2of5, Standard2of5, EAN13, EAN8, UPCA, UPCE, ISBN, ISSN, ISMN.
      """

      def __init__(self, javaClass):
            self._space = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self._space = Unit(self.getJavaClass().getSupplementSpace())

      def getSupplementData(self):
            """!
        Supplement data following BarCode.
            """
            return self.getJavaClass().getSupplementData()

      def setSupplementData(self, value):
            """!
         Supplement data following BarCode.
            """
            self.getJavaClass().setSupplementData(value)

      def getSupplementSpace(self):
            """!
        Space between main the BarCode and supplement BarCode in Unit value.
            @exception IllegalArgumentException
            The Space parameter value is less than 0.
            """
            return self._space

      def toString(self):
            """!
        Returns a human-readable string representation of this SupplementParameters.
            @return A string that represents this SupplementParameters.
            """
            return self.getJavaClass().toString()


class MaxiCodeParameters(Assist.BaseJavaClass):
      """!
      MaxiCode parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getMaxiCodeEncodeMode(self):
            """!
         Gets a MaxiCode encode mode.
            """
            return self.getJavaClass().getMaxiCodeEncodeMode()

      def setMaxiCodeEncodeMode(self, value):
            """!
         Sets a MaxiCode encode mode.
            """
            self.getJavaClass().setMaxiCodeEncodeMode(value)

      def getAspectRatio(self):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
          Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def toString(self):
            """!
         Returns a human-readable string representation of this MaxiCodeParameters.
            @return A string that represents this MaxiCodeParameters.
            """
            return self.getJavaClass().toString()


class AztecParameters(Assist.BaseJavaClass):
      """!
      Aztec parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getAztecErrorLevel(self):
            """!
          Level of error correction of Aztec types of barcode.
            Value should between 10 to 95.
            """
            return self.getJavaClass().getAztecErrorLevel()

      def setAztecErrorLevel(self, value):
            """!
            Level of error correction of Aztec types of barcode.
            Value should between 10 to 95.
            """
            self.getJavaClass().setAztecErrorLevel(value)

      def getAztecSymbolMode(self):
            """!
         Gets or sets a Aztec Symbol mode.
            Default value: AztecSymbolMode.AUTO.
            """
            return AztecSymbolMode(self.getJavaClass().getAztecSymbolMode())

      def setAztecSymbolMode(self, value):
            """!
         Gets or sets a Aztec Symbol mode.
            Default value: AztecSymbolMode.AUTO.
            """
            self.getJavaClass().setAztecSymbolMode(value.value)

      def getAspectRatio(self):
            """!
          Height/Width ratio of 2D BarCode module.
            """
            return self.getJavaClass().getAspectRatio()

      def setAspectRatio(self, value):
            """!
        Height/Width ratio of 2D BarCode module.
            """
            self.getJavaClass().setAspectRatio(value)

      def getCodeTextEncoding(self):
            """!
         Gets the encoding of codetext.
            Default value: UTF-8
            """
            return self.getJavaClass().getCodeTextEncoding()

      def setCodeTextEncoding(self, value):
            """!
        Sets the encoding of codetext.
            Default value: UTF-8
            """
            self.getJavaClass().setCodeTextEncoding(value)

      def toString(self):
            """!
        Returns a human-readable string representation of this AztecParameters.
            @return string that represents this AztecParameters.
            """
            return self.getJavaClass().toString()


class CodabarParameters(Assist.BaseJavaClass):
      """!
      Codabar parameters.
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def init(self):
            pass

      def getCodabarChecksumMode(self):
            """!
         Get the checksum algorithm for Codabar barcodes.
            Default value: CodabarChecksumMode.MOD_16.
            To enable checksum calculation set value EnableChecksum.YES to property EnableChecksum.
            See CodabarChecksumMode.
            """
            return CodabarChecksumMode(self.getJavaClass().getCodabarChecksumMode())

      def setCodabarChecksumMode(self, value):
            """!
     Set the checksum algorithm for Codabar barcodes.
            Default value: CodabarChecksumMode.MOD_16.
            To enable checksum calculation set value EnableChecksum.YES to property EnableChecksum.
            See CodabarChecksumMode.
            """
            self.getJavaClass().setCodabarChecksumMode(value.value)

      def getCodabarStartSymbol(self):
            """!
    Start symbol (character) of Codabar symbology.
            Default value: CodabarSymbol.A
            """
            return CodabarSymbol(self.getJavaClass().getCodabarStartSymbol())

      def setCodabarStartSymbol(self, value):
            """!
      Start symbol (character) of Codabar symbology.
            Default value: CodabarSymbol.A
            """
            self.getJavaClass().setCodabarStartSymbol(value.value)

      def getCodabarStopSymbol(self):
            """!
      Stop symbol (character) of Codabar symbology.
            Default value: CodabarSymbol.A
            """
            return CodabarSymbol(self.getJavaClass().getCodabarStopSymbol())

      def setCodabarStopSymbol(self, value):
            """!
         Stop symbol (character) of Codabar symbology.
            Default value: CodabarSymbol.A
            """
            self.getJavaClass().setCodabarStopSymbol(value.value)

      def toString(self):
            """!
                 Returns a human-readable string representation of this CodabarParameters.
            @return A string that represents this CodabarParameters.
            """
            return self.getJavaClass().toString()


class CouponParameters(Assist.BaseJavaClass):
      """!
          Coupon parameters. Used for UpcaGs1DatabarCoupon, UpcaGs1Code128Coupon.
      """

      def __init__(self, javaClass):
            self._space = None
            super().__init__(javaClass)
            self.init()

      def init(self):
            self._space = Unit(self.getJavaClass().getSupplementSpace())

      def getSupplementSpace(self):
            """!
        Space between main the BarCode and supplement BarCode in Unit value.
            @exception IllegalArgumentException
            The Space parameter value is less than 0.
            """
            return self._space

      def setSupplementSpace(self, value):
            """!
         Space between main the BarCode and supplement BarCode in Unit value.
            @exception IllegalArgumentException
            The Space parameter value is less than 0.
            """
            self.getJavaClass().setSupplementSpace(value.getJavaClass())
            self._space = value

      def toString(self):
            """!
         Returns a human-readable string representation of this CouponParameters.
            @return A string that represents this CouponParameters.
            """
            return self.getJavaClass().toString()


class FontUnit(Assist.BaseJavaClass):
      """!
       Defines a particular format for text, including font face, size, and style attributes
       where size in Unit value property.

       This sample shows how to create and save a BarCode image.
       \code
        generator = BarcodeGenerator(EncodeTypes.CODE_128)
        generator.getParameters().getCaptionAbove().setText("CAPTION ABOOVE")
        generator.getParameters().getCaptionAbove().setVisible(true)
        generator.getParameters().getCaptionAbove().getFont().setStyle(FontStyle.ITALIC)
        generator.getParameters().getCaptionAbove().getFont().getSize().setPoint(25)
       \endcode
      """

      def __init__(self, source):
            self._size = None
            super().__init__(FontUnit.initFontUnit(source))
            self.init()

      @staticmethod
      def initFontUnit(source):
            if isinstance(source, FontUnit):
                  return source.getJavaClass()
            return source

      def init(self):
            self._size = Unit(self.getJavaClass().getSize())

      def getFamilyName(self):
            """!
        Gets the face name of this Font.
            """
            return self.getJavaClass().getFamilyName()

      def setFamilyName(self, value):
            """!
         Sets the face name of this Font.
            """
            self.getJavaClass().setFamilyName(value)

      def getStyle(self):
            """!
        Gets style information for this FontUnit.
            """
            return FontStyle(self.getJavaClass().getStyle())

      def setStyle(self, value):
            """!
        Sets style information for this FontUnit.
            """
            self.getJavaClass().setStyle(value.value)

      def getSize(self):
            """!
         Gets size of this FontUnit in Unit value.
            @exception IllegalArgumentException
            The Size parameter value is less than or equal to 0.
            """
            return self._size


class ExtCodetextBuilder(Assist.BaseJavaClass):
      """!
      Helper class for automatic codetext generation of the Extended Codetext Mode
      """

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def clear(self):
            """!
                Clears extended codetext items
            """
            self.getJavaClass().clear()

      def addPlainCodetext(self, codetext):
            """!
        Adds plain codetext to the extended codetext items

            @param codetext Codetext in unicode to add as extended codetext item
            """
            self.getJavaClass().addPlainCodetext(codetext)

      def addECICodetext(self, ECIEncoding, codetext):
            """!
         Adds codetext with Extended Channel Identifier

            @param ECIEncoding Extended Channel Identifier
            @param codetext    Codetext in unicode to add as extended codetext item with Extended Channel Identifier
            """
            self.getJavaClass().addECICodetext(ECIEncoding.value, codetext)

      def getExtendedCodetext(self):
            """!
        Generate extended codetext from generation items list

            @return Return string of extended codetext
            """
            return self.getJavaClass().getExtendedCodetext()


class QrExtCodetextBuilder(ExtCodetextBuilder):
      """!
       Extended codetext generator for 2D QR barcodes for ExtendedCodetext Mode of QREncodeMode</p>

       Use Display2DText property of BarCodeBuilder to set visible text to removing managing characters.</p>

       Example how to generate FNC1 first position for Extended Mode

       \code
         //create codetext
         lTextBuilder = QrExtCodetextBuilder()
         lTextBuilder.addFNC1FirstPosition()
         lTextBuilder.addPlainCodetext("000%89%%0")
         lTextBuilder.addFNC1GroupSeparator()
         lTextBuilder.addPlainCodetext("12345&ltFNC1&gt")
         #generate codetext
         lCodetext = lTextBuilder.getExtendedCodetext()
       \endcode

       Example how to generate FNC1 second position for Extended Mode
       \code
          #create codetext
          lTextBuilder = QrExtCodetextBuilder()
          lTextBuilder.addFNC1SecondPosition("12")
          lTextBuilder.addPlainCodetext("TRUE3456")
          #generate codetext
          lCodetext = lTextBuilder.getExtendedCodetext()
       \endcode

       Example how to generate multi ECI mode for Extended Mode
      \code
          #create codetext
          lTextBuilder = QrExtCodetextBuilder()
          lTextBuilder.addECICodetext(ECIEncodings.Win1251, "Will")
          lTextBuilder.addECICodetext(ECIEncodings.UTF8, "Right")
          lTextBuilder.addECICodetext(ECIEncodings.UTF16BE, "Power")
          lTextBuilder.addPlainCodetext("t\\e\\\\st")
         #generate codetext
          lCodetext = lTextBuilder.getExtendedCodetext()
       \endcode
      """
      javaClassName = "com.aspose.mw.barcode.MwQrExtCodetextBuilder"

      def __init__(self):
            javaQrExtCodetextBuilder = jpype.JClass(self.javaClassName)
            self.javaClass = javaQrExtCodetextBuilder()
            super().__init__(self.javaClass)
            self.init()

      def init(self):
            pass

      def addFNC1FirstPosition(self):
            """!
             Adds FNC1 in first position to the extended codetext items
            """
            self.getJavaClass().addFNC1FirstPosition()

      def addFNC1SecondPosition(self, codetext):
            """!
        Adds FNC1 in second position to the extended codetext items
            @param codetext Value of the FNC1 in the second position
            """
            self.getJavaClass().addFNC1SecondPosition(codetext)

      def addFNC1GroupSeparator(self):
            """!
                Adds Group Separator (GS - '\\u001D') to the extended codetext items
            """
            self.getJavaClass().addFNC1GroupSeparator()

      def getExtendedCodetext(self):
            """!
             Generates Extended codetext from the extended codetext list.
            @return Extended codetext as string
            """
            return self.getJavaClass().getExtendedCodetext()


class QrStructuredAppendParameters(Assist.BaseJavaClass):
      """!
      QR structured append parameters.
      """

      def init(self):
            pass

      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def getParityByte(self):
            """!
            Gets the QR structured append mode parity data.
            """
            return self.getJavaClass().getParityByte()

      def setParityByte(self, value):
            """!
         Sets the QR structured append mode parity data.
            """
            self.getJavaClass().setParityByte(value)

      def getSequenceIndicator(self):
            """!
         Gets the index of the QR structured append mode barcode. Index starts from 0.
            """
            return self.getJavaClass().getSequenceIndicator()

      def setSequenceIndicator(self, value):
            """!
        Sets the index of the QR structured append mode barcode. Index starts from 0.
            """
            self.getJavaClass().setSequenceIndicator(value)

      def getTotalCount(self):
            """!
        Gets the QR structured append mode barcodes quantity. Max value is 16.
            """
            return self.getJavaClass().getTotalCount()

      def setTotalCount(self, value):
            """!
        Sets the QR structured append mode barcodes quantity. Max value is 16.
            """
            self.getJavaClass().setTotalCount(value)

      def getStateHash(self):
            return self.getJavaClass().getStateHash()


class MacroCharacter:
      NONE = 0
      """!
          None of Macro Characters are added to barcode data
      """

      MACRO_05 = 5
      """!
          05 Macro craracter is added to barcode data in first position.
          GS1 Data Identifier ISO 15434
          Character is translated to "[)>\u001E05\u001D" as decoded data header and "\u001E\u0004" as decoded data trailer.
         
              to generate autoidentified GS1 message like this "(10)123ABC(10)123ABC" in ISO 15434 format you need:
          generator = BarcodeGenerator(EncodeTypes.DATA_MATRIX, "10123ABC\u001D10123ABC")
          generator.getParameters().getBarcode().getDataMatrix().setMacroCharacters(MacroCharacter.MACRO_05)
          reader = new BarCodeReader(generator.generateBarCodeImage(), DecodeType.GS_1_DATA_MATRIX)
          for result in reader.readBarCodes():
              print("BarCode CodeText: " + result.getCodeText())
      """

      MACRO_06 = 6
      """!
           06 Macro craracter is added to barcode data in first position.
          ASC MH10 Data Identifier ISO 15434
          Character is translated to "[)>\u001E06\u001D" as decoded data header and "\u001E\u0004" as decoded data trailer.
      """


class FontStyle(Enum):
      """!
      Specifies style information applied to text.
      """

      REGULAR = 0
      """!
          Normal text
      """

      BOLD = 1
      """!
          Bold text
      """

      ITALIC = 2
      """!
           Italic text
      """

      UNDERLINE = 4
      """!
             Underlined text
      """

      STRIKEOUT = 8
      """!
            Text with a line through the middle
      """


class CodabarSymbol(Enum):
      """!
      Specifies the start or stop symbol of the Codabar barcode specification.
      """

      A = 65
      """!
          Specifies character A as the start or stop symbol of the Codabar barcode specification.
      """

      B = 66
      """!
          Specifies character B as the start or stop symbol of the Codabar barcode specification.
      """

      C = 67
      """!
          Specifies character C as the start or stop symbol of the Codabar barcode specification.
      """

      D = 68
      """!
          Specifies character D as the start or stop symbol of the Codabar barcode specification.
      """


class DataMatrixEncodeMode(Enum):
      """!
      DataMatrix encoder's encoding mode, default to AUTO
      """

      AUTO = 0
      """!
          Automatically pick up the best encode mode for datamatrix encoding
      """

      ASCII = 1
      """!
          Encodes one alphanumeric or two numeric characters per byte
      """

      FULL = 6
      """!
           Encode 8 bit values
      """

      CUSTOM = 7
      """!
          Encode with the encoding specified in BarCodeBuilder.CodeTextEncoding
      """

      C40 = 8
      """!
          Uses C40 encoding. Encodes Upper-case alphanumeric, Lower case and special characters
      """

      TEXT = 9
      """!
          Uses TEXT encoding. Encodes Lower-case alphanumeric, Upper case and special characters
      """

      EDIFACT = 10
      """!
          Uses EDIFACT encoding. Uses six bits per character, encodes digits, upper-case letters, and many punctuation marks, but has no support for lower-case letters.
      """

      ANSIX12 = 11
      """!
           Uses ANSI X12 encoding.
      """

      EXTENDED_CODETEXT = 12
      """!
          ExtendedCodetext mode allows to manually switch encodation schemes in codetext.
          Allowed encodation schemes are: EDIFACT, ANSIX12, ASCII, C40, Text, Auto.
          Extended codetext example: @"\ansix12:ANSIX12TEXT\ascii:backslash must be \\ doubled\edifact:EdifactEncodedText"
          All backslashes (\) must be doubled in text.
         
          This sample shows how to do codetext in Extended Mode.
         
          $generator = new BarcodeGenerator(EncodeTypes::DATA_MATRIX);
          $generator->setCodeText("\\ansix12:ANSIX12TEXT\\ascii:backslash must be \\\\ doubled\\edifact:EdifactEncodedText");
          $generator->getParameters()->getBarcode()->getDataMatrix().setDataMatrixEncodeMode(DataMatrixEncodeMode.EXTENDED_CODETEXT);
          $generator->getParameters()->getBarcode()->getCodeTextParameters().setTwoDDisplayText("My Text");
          $generator->save("test.png");
      """


class BorderDashStyle(Enum):
      """!
      Specifies the style of dashed border lines.
      """

      SOLID = 0
      """!
          Specifies a solid line.
      """

      DASH = 1
      """!
          Specifies a line consisting of dashes.
      """

      DOT = 2
      """!
           Specifies a line consisting of dots.
      """

      DASH_DOT = 3
      """!
           Specifies a line consisting of a repeating pattern of dash-dot.
      """

      DASH_DOT_DOT = 4
      """!
           Specifies a line consisting of a repeating pattern of dash-dot-dot.
      """


class ITF14BorderType(Enum):
      """!
      ITF14 barcode's border type
      """

      NONE = 0
      """!
          NO border enclosing the barcode
      """

      FRAME = 1
      """!
           FRAME enclosing the barcode
      """

      BAR = 2
      """!
          Tow horizontal bars enclosing the barcode
      """

      FRAME_OUT = 3
      """!
          FRAME enclosing the barcode
      """

      BAR_OUT = 4
      """!
          Tow horizontal bars enclosing the barcode
      """


class QREncodeMode(Enum):
      """!
      Encoding mode for QR barcodes. It is recomended to Use AUTO with CodeTextEncoding = Encoding.UTF8 for latin symbols or digits and UTF_8_BOM for unicode symbols.
      """

      AUTO = 0
      """!
          Encode codetext as is non-unicode charset. If there is any unicode character, the codetext will be encoded with value which is set in CodeTextEncoding.
      """

      BYTES = 1
      """!
          Encode codetext as plain bytes. If it detects any unicode character, the character will be encoded as two bytes, lower byte first.
      """

      UTF_8_BOM = 2
      """!
          Encode codetext with UTF8 encoding with first ByteOfMark character.
      """

      UTF_16_BEBOM = 3
      """!
          Encode codetext with UTF8 encoding with first ByteOfMark character. It can be problems with some barcode scaners.
      """

      ECI_ENCODING = 4
      """!
          Encode codetext with value set in the ECI_ENCODING property. It can be problems with some old (pre 2006) barcode scaners.
          Example how to use ECI encoding
              generator = BarcodeGenerator(EncodeTypes.QR)
              generator.setCodeText("12345TEXT")
              generator.getParameters().getBarcode().getQR().setQrEncodeMode(QREncodeMode.ECI_ENCODING)
              generator.getParameters().getBarcode().getQR().setQrEncodeType(QREncodeType.FORCE_QR)
              generator.getParameters().getBarcode().getQR().setQrECIEncoding(ECIEncodings.UTF8)
              generator.save("test.png", "PNG")
      """

      EXTENDED_CODETEXT = 5
      """!
          Extended Channel mode which supports FNC1 first position, FNC1 second position and multi ECI modes.
          It is better to use QrExtCodetextBuilder for extended codetext generation.
          Use Display2DText property to set visible text to removing managing characters.
          Encoding Principles:
          All symbols "\" must be doubled "\\" in the codetext.
          FNC1 in first position is set in codetext as as "&lt;FNC1&gt;"
          FNC1 in second position is set in codetext as as "&lt;FNC1(value)&gt;". The value must be single symbols (a-z, A-Z) or digits from 0 to 99.
          Group Separator for FNC1 modes is set as 0x1D character '\\u001D'
           If you need to insert "&lt;FNC1&gt;" string into barcode write it as "&lt;\FNC1&gt;"
          ECI identifiers are set as single slash and six digits identifier "\000026" - UTF8 ECI identifier
          TO disable current ECI mode and convert to default JIS8 mode zero mode ECI indetifier is set. "\000000"
          All unicode characters after ECI identifier are automatically encoded into correct character codeset.
           Example how to use FNC1 first position in Extended Mode
               textBuilder = QrExtCodetextBuilder()
               textBuilder.addPlainCodetext("000%89%%0")
               textBuilder.addFNC1GroupSeparator()
               textBuilder.addPlainCodetext("12345&lt;FNC1&gt;")
               //generate barcode
               generator = BarcodeGenerator(EncodeTypes.QR)
               generator.setCodeText($textBuilder.getExtendedCodetext())
               generator.getParameters().getBarcode().getQR().setQrEncodeMode(QREncodeMode.EXTENDED_CODETEXT)
               generator.getParameters().getBarcode().getCodeTextParameters().setTwoDDisplayText("My Text")
               generator.save("d:/test.png", "PNG")
          This sample shows how to use FNC1 second position in Extended Mode.
             //create codetext
             textBuilder = QrExtCodetextBuilder()
             textBuilder.addFNC1SecondPosition("12")
             textBuilder.addPlainCodetext("TRUE3456")
             //generate barcode
             generator = BarcodeGenerator(EncodeTypes.QR)
             generator.setCodeText($textBuilder.getExtendedCodetext())
             generator.getParameters().getBarcode().getCodeTextParameters().setTwoDDisplayText("My Text")
             generator.save("d:/test.png", "PNG")
             This sample shows how to use multi ECI mode in Extended Mode.
            //create codetext
             textBuilder = QrExtCodetextBuilder()
             textBuilder.addECICodetext(ECIEncodings.Win1251, "Will")
             textBuilder.addECICodetext(ECIEncodings.UTF8, "Right")
             textBuilder.addECICodetext(ECIEncodings.UTF16BE, "Power")
             textBuilder.addPlainCodetext("t\e\\st")
            //generate barcode
             generator = BarcodeGenerator(EncodeTypes.QR)
             generator.setCodeText($textBuilder.getExtendedCodetext())
             generator.getParameters().getBarcode().getQR().setQrEncodeMode(QREncodeMode.EXTENDED_CODETEXT)
             generator.getParameters().getBarcode().getCodeTextParameters().setTwoDDisplayText("My Text")
             generator.save("d:/test.png", "PNG")
      """


class DataMatrixEccType(Enum):
      """!
      Specify the type of the ECC to encode.
      """

      ECC_AUTO = 0
      """!
          Specifies that encoded Ecc type is defined by default Reed-Solomon error correction or ECC 200.
      """

      ECC_000 = 1
      """!
          Specifies that encoded Ecc type is defined ECC 000.
      """

      ECC_050 = 2
      """!
          Specifies that encoded Ecc type is defined ECC 050.
      """

      ECC_080 = 3
      """!
           Specifies that encoded Ecc type is defined ECC 080.
      """

      ECC_100 = 4
      """!
          Specifies that encoded Ecc type is defined ECC 100.
      """

      ECC_140 = 5
      """!
           Specifies that encoded Ecc type is defined ECC 140.
      """

      ECC_200 = 6
      """!
          Specifies that encoded Ecc type is defined ECC 200. Recommended to use.
      """


class QRVersion(Enum):
      """!
      Version of QR Code.
      From Version1 to Version40 for QR code and from M1 to M4 for MicroQr.
      """

      AUTO = 0
      """!
          Specifies to automatically pick up the best version for QR.
          This is default value.
      """

      VERSION_01 = 1
      """!
          Specifies version 1 with 21 x 21 modules.
      """

      VERSION_02 = 2
      """!
          Specifies version 2 with 25 x 25 modules.
      """

      VERSION_03 = 3
      """!
          Specifies version 3 with 29 x 29 modules
      """

      VERSION_04 = 4
      """!
           Specifies version 4 with 33 x 33 modules.
      """

      VERSION_05 = 5
      """!
           Specifies version 5 with 37 x 37 modules.
      """

      VERSION_06 = 6
      """!
           Specifies version 6 with 41 x 41 modules.
      """

      VERSION_07 = 7
      """!
          Specifies version 7 with 45 x 45 modules.
      """

      VERSION_08 = 8
      """!
          Specifies version 8 with 49 x 49 modules.
      """

      VERSION_09 = 9
      """!
           Specifies version 9 with 53 x 53 modules.
      """

      VERSION_10 = 10
      """!
          Specifies version 10 with 57 x 57 modules.
      """

      VERSION_11 = 11
      """!
          Specifies version 11 with 61 x 61 modules.
      """

      VERSION_12 = 12
      """!
          Specifies version 12 with 65 x 65 modules.
      """

      VERSION_13 = 13
      """!
           Specifies version 13 with 69 x 69 modules.
      """

      VERSION_14 = 14
      """!
          Specifies version 14 with 73 x 73 modules.
      """

      VERSION_15 = 15
      """!
           Specifies version 15 with 77 x 77 modules.
      """

      VERSION_16 = 16
      """!
          Specifies version 16 with 81 x 81 modules.
      """

      VERSION_17 = 17
      """!
           Specifies version 17 with 85 x 85 modules.
      """

      VERSION_18 = 18
      """!
          Specifies version 18 with 89 x 89 modules.
      """

      VERSION_19 = 19
      """!
          Specifies version 19 with 93 x 93 modules.
      """

      VERSION_20 = 20
      """!
           Specifies version 20 with 97 x 97 modules.
      """

      VERSION_21 = 21
      """!
           Specifies version 21 with 101 x 101 modules.
      """

      VERSION_22 = 22
      """!
           Specifies version 22 with 105 x 105 modules
      """

      VERSION_23 = 23
      """!
           Specifies version 23 with 109 x 109 modules.
      """

      VERSION_24 = 24
      """!
          Specifies version 24 with 113 x 113 modules.
      """

      VERSION_25 = 25
      """!
          Specifies version 25 with 117 x 117 modules.
      """

      VERSION_26 = 26
      """!
           Specifies version 26 with 121 x 121 modules.
      """

      VERSION_27 = 27
      """!
          Specifies version 27 with 125 x 125 modules.
      """

      VERSION_28 = 28
      """!
           Specifies version 28 with 129 x 129 modules.
      """

      VERSION_29 = 29
      """!
          Specifies version 29 with 133 x 133 modules.
      """

      VERSION_30 = 30
      """!
           Specifies version 30 with 137 x 137 modules.
      """

      VERSION_31 = 31
      """!
           Specifies version 31 with 141 x 141 modules.
      """

      VERSION_32 = 32
      """!
           Specifies version 32 with 145 x 145 modules.
      """

      VERSION_33 = 33
      """!
             Specifies version 33 with 149 x 149 modules.
      """

      VERSION_34 = 34
      """!
           Specifies version 34 with 153 x 153 modules.
      """

      VERSION_35 = 35
      """!
          Specifies version 35 with 157 x 157 modules.
      """

      VERSION_36 = 36
      """!
          Specifies version 36 with 161 x 161 modules.
      """

      VERSION_37 = 37
      """!
            Specifies version 37 with 165 x 165 modules
      """

      VERSION_38 = 38
      """!
           Specifies version 38 with 169 x 169 modules.
      """

      VERSION_39 = 39
      """!
          Specifies version 39 with 173 x 173 modules.
      """

      VERSION_40 = 40
      """!
            Specifies version 40 with 177 x 177 modules.
      """

      VERSION_M1 = 101
      """!
          Specifies version M1 for Micro QR with 11 x 11 modules.
      """

      VERSION_M2 = 102
      """!
           Specifies version M2 for Micro QR with 13 x 13 modules.
      """

      VERSION_M3 = 103
      """!
          Specifies version M3 for Micro QR with 15 x 15 modules.
      """

      VERSION_M4 = 104
      """!
            Specifies version M4 for Micro QR with 17 x 17 modules.
      """


class AztecSymbolMode(Enum):
      """!
      Specifies the Aztec symbol mode.

           generator = BarcodeGenerator(EncodeTypes.AZTEC)
           generator.setCodeText("125")
           generator.getParameters().getBarcode().getAztec().setAztecSymbolMode(AztecSymbolMode.RUNE)
           generator.save("test.png", "PNG")
      """

      AUTO = 0
      """!
           Specifies to automatically pick up the best symbol (COMPACT or FULL-range) for Aztec.
          This is default value.
      """

      COMPACT = 1
      """!
           Specifies the COMPACT symbol for Aztec.
          Aztec COMPACT symbol permits only 1, 2, 3 or 4 layers.
      """

      FULL_RANGE = 2
      """!
           Specifies the FULL-range symbol for Aztec.
          Aztec FULL-range symbol permits from 1 to 32 layers.
      """

      RUNE = 3
      """!
          Specifies the RUNE symbol for Aztec.
          Aztec Runes are a series of small but distinct machine-readable marks. It permits only number value from 0 to 255.
      """


class Pdf417ErrorLevel(Enum):
      """!
      pdf417 barcode's error correction level, from level 0 to level 9, level 0 means no error correction, level 9 means best error correction
      """

      LEVEL_0 = 0
      """!
          level = 0.
      """

      LEVEL_1 = 1
      """!
          level = 1.
      """

      LEVEL_2 = 2
      """!
          level = 2.
      """

      LEVEL_3 = 3
      """!
          level = 3.
      """

      LEVEL_4 = 4
      """!
          level = 4.
      """

      LEVEL_5 = 5
      """!
           level = 5.
      """

      LEVEL_6 = 6
      """!
          level = 6.
      """

      LEVEL_7 = 7
      """!
           level = 7.
      """

      LEVEL_8 = 8
      """!
          level = 8.
      """


class Pdf417CompactionMode(Enum):
      """!
      Pdf417 barcode's compation mode
      """

      AUTO = 0
      """!
          auto detect compation mode
      """

      TEXT = 1
      """!
          text compaction
      """

      NUMERIC = 2
      """!
          numeric compaction mode
      """

      BINARY = 3
      """!
           binary compaction mode
      """


class QRErrorLevel(Enum):
      """!
      Level of Reed-Solomon error correction. From low to high: LEVEL_L, LEVEL_M, LEVEL_Q, LEVEL_H.
      """

      LEVEL_L = 0
      """!
          Allows recovery of 7% of the code text
      """

      LEVEL_M = 1
      """!
           Allows recovery of 15% of the code text
      """

      LEVEL_Q = 2
      """!
          Allows recovery of 25% of the code text
      """

      LEVEL_H = 3
      """!
          Allows recovery of 30% of the code text
      """


class QREncodeType(Enum):
      """!
      QR / MicroQR selector mode. Select FORCE_QR for standard QR symbols, AUTO for MicroQR.
      FORCE_MICRO_QR is used for strongly MicroQR symbol generation if it is possible.
      """

      AUTO = 0
      """!
          Mode starts barcode version negotiation from MicroQR V1
      """

      FORCE_QR = 1
      """!
          Mode starts barcode version negotiation from QR V1
      """

      FORCE_MICRO_QR = 2
      """!
          Mode starts barcode version negotiation from from MicroQR V1 to V4. If data cannot be encoded into MicroQR, exception is thrown.
      """


class CodabarChecksumMode(Enum):
      """!
      Specifies the checksum algorithm for Codabar
      """

      MOD_10 = 0
      """!
          Specifies Mod 10 algorithm for Codabar.
      """

      MOD_16 = 1
      """!
          Specifies Mod 16 algorithm for Codabar (recomended AIIM).
      """


class CodeLocation(Enum):
      """!
          Codetext location
      """

      BELOW = 0
      """!
          Codetext below barcode.
      """

      ABOVE = 1
      """!
          Codetext above barcode.
      """

      NONE = 2
      """!
          Hide codetext.
      """


class FontMode(Enum):
      """!
          Font size mode.
      """

      AUTO = 0
      """!
          Automatically calculate Font size based on barcode size.
      """

      MANUAL = 1
      """!
          Use Font sized defined by user.
      """


class TextAlignment(Enum):
      """!
          Text alignment.
      """

      LEFT = 0
      """!
          Left position.
      """

      CENTER = 1
      """!
          Center position.
      """

      RIGHT = 2
      """!
          Right position.
      """


class AutoSizeMode(Enum):
      """!
      <p/>Specifies the different types of automatic sizing modes.
      <p/>Default value is AutoSizeMode.NONE.
      <p/> This sample shows how to create and save a BarCode image.

           generator = BarcodeGenerator(EncodeTypes.DATA_MATRIX)
           generator.setAutoSizeMode(AutoSizeMode.NEAREST)
           generator.getBarCodeWidth().setMillimeters(50)
           generator.getBarCodeHeight().setInches(1.3f)
           generator.save("test.png", "PNG")
      """

      NONE = 0
      """!
           Automatic resizing is disabled. Default value.
      """

      NEAREST = 1
      """!
          Barcode resizes to nearest lowest possible size
          which are specified by BarCodeWidth and BarCodeHeight properties.
      """

      INTERPOLATION = 2
      """!
           Resizes barcode to specified size with little scaling
           but it can be little damaged in some cases
           because using interpolation for scaling.
           Size can be specified by BarcodeGenerator.BarCodeWidth
           and BarcodeGenerator.BarCodeHeight properties.
         
           This sample shows how to create and save a BarCode image in Scale mode.
         
               generator = BarcodeGenerator( EncodeTypes.DATA_MATRIX)
               generator.getParameters().getBarcode().setAutoSizeMode(AutoSizeMode.INTERPOLATION)
               generator.getParameters().getBarcode().getBarCodeWidth().setMillimeters(50)
               generator.getParameters().getBarcode().getBarCodeHeight().setInches(1.3)
               generator.save("test.png", "PNG)
      """


class GraphicsUnit(Enum):
      """!
     Specifies the unit of measure for the given data.
      """

      WORLD = 0
      """!
          Specifies the world coordinate system unit as the unit of measure.
      """

      DISPLAY = 1
      """!
          Specifies the unit of measure of the display device. Typically pixels for video displays, and 1/100 inch for printers.
      """

      PIXEL = 2
      """!
              Specifies a device pixel as the unit of measure.
      """

      POINT = 3
      """!
          Specifies a printer's point  = 1/72 inch) as the unit of measure.
      """

      INCH = 4
      """!
          Specifies the inch as the unit of measure.
      """

      DOCUMENT = 5
      """!
          Specifies the document unit  = 1/300 inch) as the unit of measure.
      """

      MILLIMETER = 6
      """!
          Specifies the millimeter as the unit of measure.
      """


class EncodeTypes(Enum):
      """!
      Specifies the type of barcode to encode.
      """

      NONE = -1
      """!
          Unspecified encode type.
      """

      CODABAR = 0
      """!
          Specifies that the data should be encoded with CODABAR barcode specification
      """

      CODE_11 = 1
      """!
          Specifies that the data should be encoded with CODE 11 barcode specification
      """

      CODE_39_STANDARD = 2
      """!
          Specifies that the data should be encoded with Standard CODE 39 barcode specification
      """

      CODE_39_EXTENDED = 3
      """!
          Specifies that the data should be encoded with Extended CODE 39 barcode specification
      """

      CODE_93_STANDARD = 4
      """!
          Specifies that the data should be encoded with Standard CODE 93 barcode specification
      """

      CODE_93_EXTENDED = 5
      """!
          Specifies that the data should be encoded with Extended CODE 93 barcode specification
      """

      CODE_128 = 6
      """!
          Specifies that the data should be encoded with CODE 128 barcode specification
      """

      GS_1_CODE_128 = 7
      """!
      Specifies that the data should be encoded with GS1 Code 128 barcode specification. The codetext must contains parentheses for AI.
      """

      EAN_8 = 8
      """!
          Specifies that the data should be encoded with EAN-8 barcode specification
      """

      EAN_13 = 9
      """!
          Specifies that the data should be encoded with EAN-13 barcode specification
      """

      EAN_14 = 10
      """!
          Specifies that the data should be encoded with EAN14 barcode specification
      """

      SCC_14 = 11
      """!
          Specifies that the data should be encoded with SCC14 barcode specification
      """

      SSCC_18 = 12
      """!
          Specifies that the data should be encoded with SSCC18 barcode specification
      """

      UPCA = 13
      """!
          Specifies that the data should be encoded with UPC-A barcode specification
      """

      UPCE = 14
      """!
          Specifies that the data should be encoded with UPC-E barcode specification
      """

      ISBN = 15
      """!
          Specifies that the data should be encoded with isBN barcode specification
      """

      ISSN = 16
      """!
          Specifies that the data should be encoded with ISSN barcode specification
      """

      ISMN = 17
      """!
          Specifies that the data should be encoded with ISMN barcode specification
      """

      STANDARD_2_OF_5 = 18
      """!
          Specifies that the data should be encoded with Standard 2 of 5 barcode specification
      """

      INTERLEAVED_2_OF_5 = 19
      """!
          Specifies that the data should be encoded with INTERLEAVED 2 of 5 barcode specification
      """

      MATRIX_2_OF_5 = 20
      """!
          Represents Matrix 2 of 5 BarCode
      """

      ITALIAN_POST_25 = 21
      """!
          Represents Italian Post 25 barcode.
      """

      IATA_2_OF_5 = 22
      """!
          Represents IATA 2 of 5 barcode.IATA (International Air Transport Assosiation) uses this barcode for the management of air cargo.
      """

      ITF_14 = 23
      """!
          Specifies that the data should be encoded with ITF14 barcode specification
      """

      ITF_6 = 24
      """!
          Represents ITF-6  Barcode.
      """

      MSI = 25
      """!
          Specifies that the data should be encoded with MSI Plessey barcode specification
      """

      VIN = 26
      """!
          Represents VIN (Vehicle Identification Number) Barcode.
      """

      DEUTSCHE_POST_IDENTCODE = 27
      """!
          Represents Deutsch Post barcode, This EncodeType is also known as Identcode,CodeIdentcode,German Postal 2 of 5 Identcode,
          Deutsch Post AG Identcode, Deutsch Frachtpost Identcode,  Deutsch Post AG (DHL)
      """

      DEUTSCHE_POST_LEITCODE = 28
      """!
          Represents Deutsch Post Leitcode Barcode,also known as German Postal 2 of 5 Leitcode, CodeLeitcode, Leitcode, Deutsch Post AG (DHL).
      """

      OPC = 29
      """!
          Represents OPC(Optical Product Code) Barcode,also known as , VCA Barcode VCA OPC, Vision Council of America OPC Barcode.
      """

      PZN = 30
      """!
          Represents PZN barcode.This EncodeType is also known as Pharmacy central number, Pharmazentralnummer
      """

      CODE_16_K = 31
      """!
          Represents Code 16K barcode.
      """

      PHARMACODE = 32
      """!
          Represents Pharmacode barcode.
      """

      DATA_MATRIX = 33
      """!
          2D barcode symbology DataMatrix
      """

      QR = 34
      """!
          Specifies that the data should be encoded with QR Code barcode specification
      """

      AZTEC = 35
      """!
           Specifies that the data should be encoded with Aztec barcode specification
      """

      PDF_417 = 36
      """!
          Specifies that the data should be encoded with Pdf417 barcode specification
      """

      MACRO_PDF_417 = 37
      """!
          Specifies that the data should be encoded with MacroPdf417 barcode specification
      """

      GS_1_DATA_MATRIX = 48
      """!
          2D barcode symbology DataMatrix with GS1 string format
      """

      MICRO_PDF_417 = 55
      """!
          Specifies that the data should be encoded with MicroPdf417 barcode specification
      """

      GS_1_QR = 56
      """!
          2D barcode symbology QR with GS1 string format
      """

      MAXI_CODE = 57
      """!
          Specifies that the data should be encoded with MaxiCode barcode specification
      """

      DOT_CODE = 60
      """!
          Specifies that the data should be encoded with DotCode barcode specification
      """

      AUSTRALIA_POST = 38
      """!
          Represents Australia Post Customer BarCode
      """

      POSTNET = 39
      """!
          Specifies that the data should be encoded with Postnet barcode specification
      """

      PLANET = 40
      """!
          Specifies that the data should be encoded with Planet barcode specification
      """

      ONE_CODE = 41
      """!
          Specifies that the data should be encoded with USPS OneCode barcode specification
      """

      RM_4_SCC = 42
      """!
          Represents RM4SCC barcode. RM4SCC (Royal Mail 4-state Customer Code) is used for automated mail sort process in UK.
      """

      MAILMARK = 66
      """!
          Represents Royal Mail Mailmark barcode.
      """

      DATABAR_OMNI_DIRECTIONAL = 43
      """!
          Specifies that the data should be encoded with GS1 Databar omni-directional barcode specification.
      """

      DATABAR_TRUNCATED = 44
      """!
          Specifies that the data should be encoded with GS1 Databar truncated barcode specification.
      """

      DATABAR_LIMITED = 45
      """!
          Represents GS1 DATABAR limited barcode
      """

      DATABAR_EXPANDED = 46
      """!
          Represents GS1 Databar expanded barcode.
      """

      DATABAR_EXPANDED_STACKED = 52
      """!
          Represents GS1 Databar expanded stacked barcode.
      """

      DATABAR_STACKED = 53
      """!
          Represents GS1 Databar stacked barcode.
      """

      DATABAR_STACKED_OMNI_DIRECTIONAL = 54
      """!
          Represents GS1 Databar stacked omni-directional barcode.
      """

      SINGAPORE_POST = 47
      """!
          Specifies that the data should be encoded with Singapore Post Barcode barcode specification
      """

      AUSTRALIAN_POSTE_PARCEL = 49
      """!
          Specifies that the data should be encoded with Australian Post Domestic eParcel Barcode barcode specification
      """

      SWISS_POST_PARCEL = 50
      """!
      Specifies that the data should be encoded with Swiss Post Parcel Barcode barcode specification. Supported types: Domestic Mail, International Mail, Additional Services (new)
      """

      PATCH_CODE = 51
      """!
          Represents Patch code barcode
      """

      CODE_32 = 58
      """!
          Specifies that the data should be encoded with Code32 barcode specification
      """

      DATA_LOGIC_2_OF_5 = 59
      """!
          Specifies that the data should be encoded with DataLogic 2 of 5 barcode specification
      """

      DUTCH_KIX = 61
      """!
          Specifies that the data should be encoded with Dutch KIX barcode specification
      """

      UPCA_GS_1_CODE_128_COUPON = 62
      """!
          Specifies that the data should be encoded with UPC coupon with GS1-128 Extended Code barcode specification.
          An example of the input string:
          BarCodeBuilder.setCodetext("514141100906(8102)03"),
          where UPCA part is "514141100906", GS1Code128 part is (8102)03.
      """

      UPCA_GS_1_DATABAR_COUPON = 63
      """!
          Specifies that the data should be encoded with UPC coupon with GS1 DataBar addition barcode specification.
          An example of the input string:
          BarCodeBuilder.setCodetext("514141100906(8110)106141416543213500110000310123196000"),
          where UPCA part is "514141100906", DATABAR part is "(8110)106141416543213500110000310123196000".
          To change the caption, use barCodeBuilder.getCaptionAbove().setText("company prefix + offer code")
      """

      CODABLOCK_F = 64
      """!
           Specifies that the data should be encoded with Codablock-F barcode specification.
      """

      GS_1_CODABLOCK_F = 65
      """!
          Specifies that the data should be encoded with GS1 Codablock-F barcode specification. The codetext must contains parentheses for AI.
      """


class PatchFormat(Enum):
      """!
      PatchCode format. Choose PatchOnly to generate single PatchCode. Use page format to generate Patch page with PatchCodes as borders
      """

      PATCH_ONLY = 0
      """!
          Generates PatchCode only
      """

      A4 = 1
      """!
          Generates A4 format page with PatchCodes as borders and optional QR in the center
      """

      A4_LANDSCAPE = 2
      """!
          Generates A4 landscape format page with PatchCodes as borders and optional QR in the center
      """

      US_LETTER = 3
      """!
          Generates US letter format page with PatchCodes as borders and optional QR in the center
      """

      US_LETTER_LANDSCAPE = 4
      """!
          Generates US letter landscape format page with PatchCodes as borders and optional QR in the center
      """


class ECIEncodings(Enum):
      """!
      Extended Channel Interpretation Identifiers. It is used to tell the barcode reader details
      about the used references for encoding the data in the symbol.
      Current implementation consists all well known charset encodings.
      Currently, it is used only for QR 2D barcode.

      Example how to use ECI encoding

          generator = BarcodeGenerator(EncodeTypes.QR)
          generator.setCodeText("12345TEXT")
          generator.getParameters().getBarcode().getQR().setQrEncodeMode(QREncodeMode.ECI_ENCODING)
          generator.getParameters().getBarcode().getQR().setQrEncodeType(QREncodeType.FORCE_QR)
          generator.getParameters().getBarcode().getQR().setQrECIEncoding(ECIEncodings.UTF_8)
          generator.save("test.png", "PNG")
      """

      ISO_8859_1 = 3
      """!
          ISO/IEC 8859-1 Latin alphabet No. 1 encoding. ECI Id:"\000003"
      """

      ISO_8859_2 = 4
      """!
          ISO/IEC 8859-2 Latin alphabet No. 2 encoding. ECI Id:"\000004"
      """

      ISO_8859_3 = 5
      """!
          ISO/IEC 8859-3 Latin alphabet No. 3 encoding. ECI Id:"\000005"
      """

      ISO_8859_4 = 6
      """!
          ISO/IEC 8859-4 Latin alphabet No. 4 encoding. ECI Id:"\000006"
      """

      ISO_8859_5 = 7
      """!
           ISO/IEC 8859-5 Latin/Cyrillic alphabet encoding. ECI Id:"\000007"
      """

      ISO_8859_6 = 8
      """!
           ISO/IEC 8859-6 Latin/Arabic alphabet encoding. ECI Id:"\000008"
      """

      ISO_8859_7 = 9
      """!
          ISO/IEC 8859-7 Latin/Greek alphabet encoding. ECI Id:"\000009"
      """

      ISO_8859_8 = 10
      """!
          ISO/IEC 8859-8 Latin/Hebrew alphabet encoding. ECI Id:"\000010"
      """

      ISO_8859_9 = 11
      """!
          ISO/IEC 8859-9 Latin alphabet No. 5 encoding. ECI Id:"\000011"
      """

      ISO_8859_10 = 12
      """!
          ISO/IEC 8859-10 Latin alphabet No. 6 encoding. ECI Id:"\000012"
      """

      ISO_8859_11 = 13
      """!
           ISO/IEC 8859-11 Latin/Thai alphabet encoding. ECI Id:"\000013"
      """

      ISO_8859_13 = 15
      """!
          ISO/IEC 8859-13 Latin alphabet No. 7 (Baltic Rim) encoding. ECI Id:"\000015"
      """

      ISO_8859_14 = 16
      """!
           ISO/IEC 8859-14 Latin alphabet No. 8 (Celtic) encoding. ECI Id:"\000016"
      """

      ISO_8859_15 = 17
      """!
          ISO/IEC 8859-15 Latin alphabet No. 9 encoding. ECI Id:"\000017"
      """

      ISO_8859_16 = 18
      """!
          ISO/IEC 8859-16 Latin alphabet No. 10 encoding. ECI Id:"\000018"
      """

      Shift_JIS = 20
      """!
           Shift JIS (JIS X 0208 Annex 1 + JIS X 0201) encoding. ECI Id:"\000020"
      """

      Win1250 = 21
      """!
          Windows 1250 Latin 2 (Central Europe) encoding. ECI Id:"\000021"
      """

      Win1251 = 22
      """!
           Windows 1251 Cyrillic encoding. ECI Id:"\000022"
      """

      Win1252 = 23
      """!
           Windows 1252 Latin 1 encoding. ECI Id:"\000023"
      """

      Win1256 = 24
      """!
          Windows 1256 Arabic encoding. ECI Id:"\000024"
      """

      UTF16BE = 25
      """!
          ISO/IEC 10646 UCS-2 (High order byte first) encoding. ECI Id:"\000025"
      """

      UTF8 = 26
      """!
          ISO/IEC 10646 UTF-8 encoding. ECI Id:"\000026"
      """

      US_ASCII = 27
      """!
          ISO/IEC 646:1991 International Reference Version of ISO 7-bit coded character set encoding. ECI Id:"\000027"
      """

      Big5 = 28
      """!
          Big 5 (Taiwan) Chinese Character Set encoding. ECI Id:"\000028"
      """

      GB18030 = 29
      """!
          GB (PRC) Chinese Character Set encoding. ECI Id:"\000029"
      """

      EUC_KR = 30
      """!
           Korean Character Set encoding. ECI Id:"\000030"
      """

      NONE = 0
      """!
          <p>No Extended Channel Interpretation/p>
      """


class EnableChecksum(Enum):
      """!
          Enable checksum during generation for 1D barcodes.

          Default is treated as Yes for symbologies which must contain checksum, as No where checksum only possible.<br>
          Checksum never used: Codabar<br>
          Checksum is possible: Code39 Standard/Extended, Standard2of5, Interleaved2of5, Matrix2of5, ItalianPost25, DeutschePostIdentcode, DeutschePostLeitcode, VIN<br>
          Checksum always used: Rest symbologies
      """

      DEFAULT = 0
      """!
          If checksum is required by the specification - it will be attached.
      """

      YES = 1
      """!
           Always use checksum if possible.
      """

      NO = 2
      """!
          Do not use checksum.
      """


class Code128Emulation:
      """!
          Function codewords for Code 128 emulation. Applied for MicroPDF417 only. Ignored for PDF417 and MacroPDF417 barcodes.
      """

      NONE = 0
      """!
           No Code 128 emulation
      """

      CODE_903 = 903
      """!
          UCC/EAN-128 emulation. Text compactionmode implied.
      """

      CODE_904 = 904
      """!
          UCC/EAN-128 emulation. Numeric compactionmode implied.
      """

      CODE_905 = 905
      """!
          UCC/EAN-128 emulation. Implied '01' AI and 14-digit codetext.
      """


class BarCodeImageFormat(Enum):
      """!
          Specifies the file format of the image.
      """

      BMP = 0
      """!
           Specifies the bitmap (BMP) image format.
      """

      GIF = 1
      """!
      Specifies the Graphics Interchange Format (GIF) image format.
      """

      JPEG = 2
      """
      Specifies the Joint Photographic Experts Group (JPEG) image format.
      """

      PNG = 3
      """!
      Specifies the W3C Portable Network Graphics (PNG) image format.
      """

      TIFF = 4
      """!
      Specifies the Tagged Image File Format (TIFF) image format.
      """

      TIFF_IN_CMYK = 5
      """!
      Specifies the Tagged Image File Format (TIFF) image format in CMYK color model.
      """

      EMF = 6
      """!
      Specifies the Enhanced Metafile (EMF) image format.
      """

      SVG = 7
      """!
      Specifies the Scalable Vector Graphics (SVG) image format.
      """

class CustomerInformationInterpretingType(Enum):
      """!
          Defines the interpreting type(C_TABLE or N_TABLE) of customer information for AustralianPost BarCode.
      """

      C_TABLE = 0
      """!
          Use C_TABLE to interpret the customer information. Allows A..Z, a..z, 1..9, space and     sing.
          generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "5912345678ABCde")
          generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.C_TABLE)
          image = generator.generateBarCodeImage()
          reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
          reader.setCustomerInformationInterpretingType(CustomerInformationInterpretingType.C_TABLE)
          for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeType())
              print("BarCode CodeText: " + result.getCodeText())
      """

      N_TABLE = 1
      """!
            Use N_TABLE to interpret the customer information. Allows digits.
           generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "59123456781234567")
           generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.N_TABLE)
           image = generator.generateBarCodeImage()
           reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
           reader.setCustomerInformationInterpretingType(CustomerInformationInterpretingType.N_TABLE)
          for result in reader.readBarCodes():
              print("BarCode Type: " + result.getCodeType())
              print("BarCode CodeText: " + result.getCodeText())
      """

      OTHER = 2
      """!
            Do not interpret the customer information. Allows 0, 1, 2 or 3 symbol only.
          generator = BarcodeGenerator(EncodeTypes.AUSTRALIA_POST, "59123456780123012301230123")
          generator.getParameters().getBarcode().getAustralianPost().setAustralianPostEncodingTable(CustomerInformationInterpretingType.OTHER)
          image = generator.generateBarCodeImage()
          reader = BarCodeReader(image, DecodeType.AUSTRALIA_POST)
          reader.CustomerInformationInterpretingType = CustomerInformationInterpretingType.OTHER)
          for result in reader.readBarCodes():
             print("BarCode Type: " + result.getCodeType())
             print("BarCode CodeText: " + result.getCodeText())
      """
