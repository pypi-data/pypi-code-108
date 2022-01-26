import jpype
import base64
import io
from PIL import Image
from enum import Enum
from . import Generation, ComplexBarcode, Assist

class IComplexCodetext(Assist.BaseJavaClass):
      """!
      Interface for complex codetext used with ComplexBarcodeGenerator.
      """
      def __init__(self, javaClass):
            super().__init__(javaClass)
            self.init()

      def getConstructedCodetext(self):
            """!
            Construct codetext for complex barcode
            @return Constructed codetext
            """
            raise Assist.BarCodeException('You have to implement the method getConstructedCodetext!')

      def initFromString(self, constructedCodetext):
            """!
            Initializes instance with constructed codetext.
            @param constructedCodetext Constructed codetext.
            """
            raise Assist.BarCodeException('You have to implement the method initFromString!')

      def getBarcodeType(self):
            """!
            Gets barcode type.
            @return Barcode type.
            """
            raise Assist.BarCodeException('You have to implement the method getBarcodeType!')

class ComplexBarcodeGenerator(Assist.BaseJavaClass):
      """!
      ComplexBarcodeGenerator for backend complex barcode (e.g. SwissQR) images generation.
      This sample shows how to create and save a SwissQR image.
       swissQRCodetext = SwissQRCodetext(null);
       swissQRCodetext.getBill().setAccount("Account");
       swissQRCodetext.getBill().setBillInformation("BillInformation");
       swissQRCodetext.getBill().setBillInformation("BillInformation");
       swissQRCodetext.getBill().setAmount(1024);
       swissQRCodetext.getBill().getCreditor().setName("Creditor.Name");
       swissQRCodetext.getBill().getCreditor().setAddressLine1("Creditor.AddressLine1");
       swissQRCodetext.getBill().getCreditor().setAddressLine2("Creditor.AddressLine2");
       swissQRCodetext.getBill().getCreditor().setCountryCode("Nl");
       swissQRCodetext.getBill().setUnstructuredMessage("UnstructuredMessage");
       swissQRCodetext.getBill().setReference("Reference");
       swissQRCodetext.getBill().setAlternativeSchemes([AlternativeScheme("AlternativeSchemeInstruction1"), AlternativeScheme("AlternativeSchemeInstruction2")]);
       swissQRCodetext.getBill().setDebtor(new Address(null));
       swissQRCodetext.getBill().getDebtor().setName("Debtor.Name");
       swissQRCodetext.getBill().getDebtor().setAddressLine1("Debtor.AddressLine1");
       swissQRCodetext.getBill().getDebtor().setAddressLine2("Debtor.AddressLine2");
       swissQRCodetext.getBill().getDebtor().setCountryCode("Lux");
       cg = ComplexBarcodeGenerator(swissQRCodetext);
       res = cg.generateBarCodeImage();
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwComplexBarcodeGenerator"

      def init(self):
            self.parameters = Generation.BaseGenerationParameters(self.getJavaClass().getParameters())

      def getParameters(self):
            """!
            Generation parameters.
            """
            return self.parameters

      def __init__(self, complexCodetext):
            """!
            Creates an instance of ComplexBarcodeGenerator.
            @param complexCodetext Complex codetext
            """
            self.parameters = None
            javaComplexBarcodeGenerator = jpype.JClass(ComplexBarcodeGenerator.javaClassName)
            super().__init__(javaComplexBarcodeGenerator(complexCodetext.getJavaClass()))
            self.init()

      def generateBarCodeImage(self):
            """!
            Generates complex barcode image under current settings.
            @param value of BarCodeImageFormat (PNG, BMP, JPEG, GIF, TIFF)
            default value is BarCodeImageFormat.PNG
            @return  Pillow Image object of barcode image
            """
            bytes = base64.b64decode(str(self.javaClass.generateBarCodeImage(Generation.BarCodeImageFormat.PNG.value)))
            buf = io.BytesIO(bytes)
            return Image.open(buf)

      def save(self, imagePath, imageFormat):
            """!
            Save barcode image to specific file in specific format.
            @param filePath Path to save to.
            @param value of BarCodeImageFormat enum (PNG, BMP, JPEG, GIF, TIFF)
            generator = BarCodeGenerator(EncodeTypes.CODE_128);
            generator.save(file_path, BarCodeImageFormat.PNG);
            """
            self.generateBarCodeImage().save(imagePath, str(imageFormat))


class Address(Assist.BaseJavaClass):
      """!
      Address of creditor or debtor.
      You can either set street, house number, postal code and town (type structured address)
      or address line 1 and 2 (type combined address elements). The type is automatically set
      once any of these fields is set. Before setting the fields, the address type is undetermined.
      If fields of both types are set, the address type becomes conflicting.
      Name and country code must always be set unless all fields are empty.
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwAddress"

      def __init__(self, arg):
            super().__init__(Address.initAddress(arg))
            self.init()

      @staticmethod
      def initAddress(arg):
            if (arg == None):
                  javaAddress = jpype.JClass(Address.javaClassName)
                  return javaAddress()
            return arg

      def getType(self):
            """!
            Gets the address type.
            The address type is automatically set by either setting street / house number
            or address line 1 and 2. Before setting the fields, the address type is Undetermined.
            If fields of both types are set, the address type becomes Conflicting.
            Value: The address type.
            """
            return self.getJavaClass().getType()

      def getName(self):
            """!
            Gets the name, either the first and last name of a natural person or the
            company name of a legal person.
            Value: The name.
            """
            return self.getJavaClass().getName()

      def setName(self, value):
            """!
           Sets the name, either the first and last name of a natural person or the
           company name of a legal person.
            Value: The name.
            """
            self.getJavaClass().setName(value)

      def getAddressLine1(self):
            """!
            Gets the address line 1.
            Address line 1 contains street name, house number or P.O. box.
           Setting this field sets the address type to AddressType.CombinedElements unless it's already
            AddressType.Structured, in which case it becomes AddressType.Conflicting.
            This field is only used for combined elements addresses and is optional.
            Value: The address line 1.
            """
            return self.getJavaClass().getAddressLine1()

      def setAddressLine1(self, value):
            """!
            Sets the address line 1.
            Address line 1 contains street name, house number or P.O. box.
            Setting this field sets the address type to AddressType.CombinedElements unless it's already
            AddressType.Structured, in which case it becomes AddressType.Conflicting.
            This field is only used for combined elements addresses and is optional.
            Value: The address line 1.
            """
            self.getJavaClass().setAddressLine1(value)

      def getAddressLine2(self):
            """!
            Gets the address line 2.
            Address line 2 contains postal code and town.
            Setting this field sets the address type to AddressType.CombinedElements unless it's already
            AddressType.Structured, in which case it becomes AddressType.Conflicting.
            This field is only used for combined elements addresses. For this type, it's mandatory.
             Value: The address line 2.
            """
            return self.getJavaClass().getAddressLine2()

      def setAddressLine2(self, value):
            """!
            Sets the address line 2.
            Address line 2 contains postal code and town.
           Setting this field sets the address type to AddressType.CombinedElements unless it's already
            AddressType.Structured, in which case it becomes AddressType.Conflicting.
           This field is only used for combined elements addresses. For this type, it's mandatory.
           Value: The address line 2.
            """
            self.getJavaClass().setAddressLine2(value)

      def getStreet(self):
            """!
           Gets the street.
          The street must be speicfied without house number.
          Setting this field sets the address type to AddressType.Structured unless it's already
          AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
          This field is only used for structured addresses and is optional.
          Value: The street.
            """
            return self.getJavaClass().getStreet()

      def setStreet(self, value):
            """!
            Sets the street.
            The street must be speicfied without house number.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses and is optional.
            Value: The street.
            """
            self.getJavaClass().setStreet(value)

      def getHouseNo(self):
            """!
            Gets the house number.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses and is optional.
            Value: The house number.
            """
            return self.getJavaClass().getHouseNo()

      def setHouseNo(self, value):
            """!
            Sets the house number.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses and is optional.
            Value: The house number.
            """
            self.getJavaClass().setHouseNo(value)

      def getPostalCode(self):
            """!
            Gets the postal code.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses. For this type, it's mandatory.
            Value: The postal code.
            """
            return self.getJavaClass().getPostalCode()

      def setPostalCode(self, value):
            """!
            Sets the postal code.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses. For this type, it's mandatory.
            Value: The postal code.
            """
            self.getJavaClass().setPostalCode(value)

      def getTown(self):
            """!
            Gets the town or city.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses. For this type, it's mandatory.
            Value: The town or city.
            """
            return self.getJavaClass().getTown()

      def setTown(self, value):
            """!
            Sets the town or city.
            Setting this field sets the address type to AddressType.Structured unless it's already
            AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
            This field is only used for structured addresses. For this type, it's mandatory.
            Value: The town or city.
            """
            self.getJavaClass().setTown(value)

      def getCountryCode(self):
            """!
            Gets the two-letter ISO country code.
            The country code is mandatory unless the entire address contains null or emtpy values.
            Value: The ISO country code.
            """
            return self.getJavaClass().getCountryCode()

      def setCountryCode(self, value):
            """!
            Sets the two-letter ISO country code.
            The country code is mandatory unless the entire address contains null or emtpy values.
            Value: The ISO country code.
            """
            self.getJavaClass().setCountryCode(value)

      def clear(self):
            """!
            Clears all fields and sets the type to AddressType.Undetermined.
            """
            self.setName(None)
            self.setAddressLine1(None)
            self.setaddressLine2(None)
            self.setStreet(None)
            self.setHouseNo(None)
            self.setPostalCode(None)
            self.setTown(None)
            self.setCountryCode(None)

      def equals(self, obj):
            """!
            Determines whether the specified object is equal to the current object.
            @return true if the specified object is equal to the current object; otherwise, false.
            @param obj The object to compare with the current object.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
            Gets the hash code for this instance.
            @return A hash code for the current object.
            """
            return self.getJavaClass().hashCode()

      def init(self):
            return


class AddressType(Enum):
      """!
      Address type
      """

      UNDETERMINED = 0
      """!
      Undetermined
      """

      STRUCTURED = 1
      """!
      Structured address
      """

      COMBINED_ELEMENTS = 2
      """!
      Combined address elements
      """

      CONFLICTING = 3
      """!
      Conflicting
      """


class AlternativeScheme(Assist.BaseJavaClass):
      """!
      Alternative payment scheme instructions
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwAlternativeScheme"

      def __init__(self, instruction):
            javaAlternativeScheme = jpype.JClass(AlternativeScheme.javaClassName)
            super().__init__(javaAlternativeScheme(instruction))

      @staticmethod
      def construct(javaClass):
            jsClass = AlternativeScheme("")
            jsClass.setJavaClass(javaClass)
            return jsClass

      def getInstruction(self):
            """!
            Gets the payment instruction for a given bill.
            The instruction consists of a two letter abbreviation for the scheme, a separator characters
            and a sequence of parameters(separated by the character at index 2).
            Value: The payment instruction.
            """
            return self.getJavaClass().getInstruction()

      def setInstruction(self, value):
            """!
            Gets the payment instruction for a given bill.
            The instruction consists of a two letter abbreviation for the scheme, a separator characters
            and a sequence of parameters(separated by the character at index 2).
            Value: The payment instruction.
            """
            self.getJavaClass().setInstruction(value)

      def equals(self, obj):
            """!
            Determines whether the specified object is equal to the current object.
            @return true if the specified object is equal to the current object; otherwise, false.
            @param obj The object to compare with the current object.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
            Gets the hash code for this instance.
            @return  hash code for the current object.
            """
            return self.getJavaClass().hashCode()

      def init(self):
            return


class ComplexCodetextReader(Assist.BaseJavaClass):
      """!
      ComplexCodetextReader decodes codetext to specified complex barcode type.
       This sample shows how to recognize and decode SwissQR image.
          cr = BarCodeReader("SwissQRCodetext.png", DecodeType.QR);
          cr.read();
          result = ComplexCodetextReader.tryDecodeSwissQR(cr.getCodeText(false));
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwComplexCodetextReader"

      @staticmethod
      def tryDecodeSwissQR(encodedCodetext):
            """!
            Decodes SwissQR codetext.
            @return decoded SwissQRCodetext or null.
            @param encodedCodetext encoded codetext
            """
            javaPythonComplexCodetextReader = jpype.JClass(ComplexCodetextReader.javaClassName)
            return SwissQRCodetext.construct(javaPythonComplexCodetextReader.tryDecodeSwissQR(encodedCodetext))

      @staticmethod
      def tryDecodeMailmark2D(encodedCodetext):
            """!
            Decodes Royal Mail Mailmark 2D codetext.
            @param encodedCodetext encoded codetext
            @return decoded Royal Mail Mailmark 2D or null.
            """
            javaPythonComplexCodetextReader = jpype.JClass(ComplexCodetextReader.javaClassName)
            return Mailmark2DCodetext.construct(javaPythonComplexCodetextReader.tryDecodeMailmark2D(encodedCodetext))

      @staticmethod
      def tryDecodeMailmark(encodedCodetext):
            """!
            Decodes Mailmark Barcode C and L codetext.
            @param encodedCodetext encoded codetext
            @return Decoded Mailmark Barcode C and L or null.
            """
            res = ComplexBarcode.MailmarkCodetext(None)
            try:
                  res.initFromString(encodedCodetext)
            except Exception as e:
                  return None
            return res

class QrBillStandardVersion(Enum):
      """!
      SwissQR bill standard version
      """

      V2_0 = 0
      """!
      Version 2.0
      """


class SwissQRBill(Assist.BaseJavaClass):
      """!
      SwissQR bill data
      """

      def init(self):
            self.creditor = Address(self.getJavaClass().getCreditor())
            self.debtor = Address(self.getJavaClass().getDebtor())

      def __init__(self, javaClass):
            self.creditor = None
            self.debtor = None
            super().__init__(javaClass)
            self.init()

      @staticmethod
      def convertAlternativeSchemes(javaAlternativeSchemes):
            alternativeSchemes = []
            i = 0
            while i < javaAlternativeSchemes.size():
                  alternativeSchemes.append(AlternativeScheme.construct(javaAlternativeSchemes.get(i)))
                  i += 1
            return alternativeSchemes

      def getVersion(self):
            """!
            Gets the version of the SwissQR bill standard.
            Value: The SwissQR bill standard version.
            """
            return QrBillStandardVersion(self.getJavaClass().getVersion())

      def setVersion(self, value):
            """!
            Sets the version of the SwissQR bill standard.
            Value: The SwissQR bill standard version.
            """
            self.getJavaClass().setVersion(value.value)

      def getAmount(self):
            """!
            Gets the payment amount.
            Valid values are between 0.01 and 999,999,999.99.
            Value: The payment amount.
            """
            return self.getJavaClass().getAmount()

      def setAmount(self, value):
            """!
            Sets the payment amount.
            Valid values are between 0.01 and 999,999,999.99.
            Value: The payment amount.
            """
            self.getJavaClass().setAmount(value)

      def getCurrency(self):
            """!
            Gets the payment currency.
            Valid values are "CHF" and "EUR".
            Value: The payment currency.
            """
            return self.getJavaClass().getCurrency()

      def setCurrency(self, value):
            """!
            Sets the payment currency.
            Valid values are "CHF" and "EUR".
            Value: The payment currency.
            """
            self.getJavaClass().setCurrency(value)

      def getAccount(self):
            """!
            Gets the creditor's account number.
            Account numbers must be valid IBANs of a bank of Switzerland or
            Liechtenstein. Spaces are allowed in the account number.
            Value: The creditor account number.
            """
            return self.getJavaClass().getAccount()

      def setAccount(self, value):
            """!
            Sets the creditor's account number.
            Account numbers must be valid IBANs of a bank of Switzerland or
            Liechtenstein. Spaces are allowed in the account number.
            Value: The creditor account number.
            """
            self.getJavaClass().setAccount(value)

      def getCreditor(self):
            """!
            Gets the creditor address.
            Value: The creditor address.
            """
            return self.creditor

      def setCreditor(self, value):
            """!
            Sets the creditor address.
            Value: The creditor address.
            """
            self.creditor = value
            self.getJavaClass().setCreditor(value.getJavaClass())

      def getReference(self):
            """!
            Gets the creditor payment reference.
            The reference is mandatory for SwissQR IBANs, i.e.IBANs in the range
            CHxx30000xxxxxx through CHxx31999xxxxx.
            If specified, the reference must be either a valid SwissQR reference
            (corresponding to ISR reference form) or a valid creditor reference
             according to ISO 11649 ("RFxxxx"). Both may contain spaces for formatting.
            Value: The creditor payment reference.
            """
            return self.getJavaClass().getReference()

      def setReference(self, value):
            """!
            Sets the creditor payment reference.
            The reference is mandatory for SwissQR IBANs, i.e.IBANs in the range
            CHxx30000xxxxxx through CHxx31999xxxxx.
            If specified, the reference must be either a valid SwissQR reference
            (corresponding to ISR reference form) or a valid creditor reference
            according to ISO 11649 ("RFxxxx"). Both may contain spaces for formatting.
            Value: The creditor payment reference.
            """
            self.getJavaClass().setReference(value)

      def createAndSetCreditorReference(self, rawReference):
            """!
            Creates and sets a ISO11649 creditor reference from a raw string by prefixing
            the String with "RF" and the modulo 97 checksum.
            Whitespace is removed from the reference
            @exception ArgumentException rawReference contains invalid characters.
            @param rawReference The raw reference.
            """
            self.getJavaClass().createAndSetCreditorReference(rawReference)

      def getDebtor(self):
            """!
            Gets the debtor address.
            The debtor is optional. If it is omitted, both setting this field to
            null or setting an address with all null or empty values is ok.
            Value: The debtor address.
            """
            return self.debtor

      def setDebtor(self, value):
            """!
            Sets the debtor address.
            The debtor is optional. If it is omitted, both setting this field to
            null or setting an address with all null or empty values is ok.
            Value: The debtor address.
            """
            self.debtor = value
            self.getJavaClass().setDebtor(value.getJavaClass())

      def getUnstructuredMessage(self):
            """!
            Gets the additional unstructured message.
            Value: The unstructured message.
            """
            return self.getJavaClass().getUnstructuredMessage()

      def setUnstructuredMessage(self, value):
            """!
            Sets the additional unstructured message.
            Value: The unstructured message.
            """
            self.getJavaClass().setUnstructuredMessage(value)

      def getBillInformation(self):
            """!
            Gets the additional structured bill information.
            Value: The structured bill information.
            """
            return self.getJavaClass().getBillInformation()

      def setBillInformation(self, value):
            """!
            Sets the additional structured bill information.
            Value: The structured bill information.
            """
            self.getJavaClass().setBillInformation(value)

      def getAlternativeSchemes(self):
            """!
            Gets the alternative payment schemes.
            A maximum of two schemes with parameters are allowed.
            Value: The alternative payment schemes.
            """
            return SwissQRBill.convertAlternativeSchemes(self.getJavaClass().getAlternativeSchemes());

      def setAlternativeSchemes(self, value):
            """!
            Sets the alternative payment schemes.
            A maximum of two schemes with parameters are allowed.
            Value: The alternative payment schemes.
            """
            ArrayList = jpype.JClass('java.util.ArrayList')
            javaArray = ArrayList()
            i = 0
            while (i < len(value)):
                  javaArray.add(value[i].getJavaClass())
                  i += 1
            self.getJavaClass().setAlternativeSchemes(javaArray)

      def equals(self, obj):
            """!
           Determines whether the specified object is equal to the current object.
           @return true if the specified object is equal to the current object; otherwise, false.
           @param obj The object to compare with the current object.
            """
            return self.getJavaClass().equals(obj.getJavaClass())

      def hashCode(self):
            """!
            Gets the hash code for this instance.
           @return A hash code for the current object.
            """
            return self.getJavaClass().hashCode()


class SwissQRCodetext(IComplexCodetext):
      """!
      Class for encoding and decoding the text embedded in the SwissQR code.
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwSwissQRCodetext"

      def init(self):
            self.bill = SwissQRBill(self.getJavaClass().getBill())

      def getBill(self):
            """!
            SwissQR bill data
            """
            return self.bill

      def __init__(self, bill):
            """!
            Creates an instance of SwissQRCodetext.
            @param bill SwissQR bill data
            @throws BarCodeException
            """
            javaClass = jpype.JClass(SwissQRCodetext.javaClassName)

            self.bill = None
            javaBill = None

            if bill == None:
                  javaBill = javaClass()
            else:
                  javaBill = javaClass(bill.getJavaClass())
            super().__init__(javaBill)
            self.init()

      @staticmethod
      def construct(javaClass):
            phpClass = SwissQRCodetext(None)
            phpClass.setJavaClass(javaClass)
            return phpClass

      def getConstructedCodetext(self):
            """!
            Construct codetext from SwissQR bill data
            @return Constructed codetext
            """
            return self.getJavaClass().getConstructedCodetext()

      def initFromString(self, constructedCodetext):
            """!
            Initializes Bill with constructed codetext.
            @param constructedCodetext Constructed codetext.
            """
            self.getJavaClass().initFromString(constructedCodetext)
            self.init()

      def getBarcodeType(self):
            """!
            Gets barcode type.
            @return Barcode type.
            """
            return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())

class MailmarkCodetext(IComplexCodetext):
      """!
      Class for encoding and decoding the text embedded in the 4-state Royal Mailmark code.
      """
      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwMailmarkCodetext"

      def getFormat(self):
            """!
            "0" – Null or Test
            "1" – Letter
            "2" – Large Letter
            """
            return self.getJavaClass().getFormat()

      def setFormat(self, value):
            """!
            "0" – Null or Test
            "1" – LetterN
            "2" – Large Letter
            """
            self.getJavaClass().setFormat(value)

      def getVersionID(self):
            """!
            Currently "1" – For Mailmark barcode (0 and 2 to 9 and A to Z spare for future use)
            :return:
            """
            return self.getJavaClass().getVersionID()

      def setVersionID(self, value):
            """!
            Currently "1" – For Mailmark barcode (0 and 2 to 9 and A to Z spare for future use)
            """
            self.getJavaClass().setVersionID(value)

      def getClass_(self):
            """!
            "0" - Null or Test
            "1" - 1C (Retail)
            "2" - 2C (Retail)
            "3" - 3C (Retail)
            "4" - Premium (RetailPublishing Mail) (for potential future use)
            "5" - Deferred (Retail)
            "6" - Air (Retail) (for potential future use)
            "7" - Surface (Retail) (for potential future use)
            "8" - Premium (Network Access)
            "9" - Standard (Network Access)
            :return:
            """
            return self.getJavaClass().getClass_()

      def setClass(self, value):
            """!
            "0" - Null or Test
            "1" - 1C (Retail)
            "2" - 2C (Retail)
            "3" - 3C (Retail)
            "4" - Premium (RetailPublishing Mail) (for potential future use)
            "5" - Deferred (Retail)
            "6" - Air (Retail) (for potential future use)
            "7" - Surface (Retail) (for potential future use)
            "8" - Premium (Network Access)
            "9" - Standard (Network Access)
            """
            self.getJavaClass().setClass(value)

      def getSupplychainID(self):
            """!
            Maximum values are 99 for Barcode C and 999999 for Barcode L.
            :return:
            """
            return self.getJavaClass().getSupplychainID()

      def setSupplychainID(self, value):
            """!
            Maximum values are 99 for Barcode C and 999999 for Barcode L.
            :param value:
            :return:
            """
            self.getJavaClass().setSupplychainID(value)

      def getItemID(self):
            """!
            Maximum value is 99999999.
            :return:
            """
            return self.getJavaClass().getItemID()

      def setItemID(self, value):
            """
            Maximum value is 99999999.
            :param value:
            :return:
            """
            self.getJavaClass().setItemID(value)

      def getDestinationPostCodePlusDPS(self):
            """
            The PC and DP must comply with a PAF format.
            Nine character string denoting international "XY11     " (note the 5 trailing spaces) or a pattern
            of characters denoting a domestic sorting code.
            A domestic sorting code consists of an outward postcode, an inward postcode, and a Delivery Point Suffix.

            :return:
            """
            return self.getJavaClass().getDestinationPostCodePlusDPS()

      def setDestinationPostCodePlusDPS(self, value):
            """
            The PC and DP must comply with a PAF format.
            Nine character string denoting international "XY11     " (note the 5 trailing spaces) or a pattern
            of characters denoting a domestic sorting code.
            A domestic sorting code consists of an outward postcode, an inward postcode, and a Delivery Point Suffix.

            :param value:
            :return:
            """
            self.getJavaClass().setDestinationPostCodePlusDPS(value)

      def __init__(self, mailmarkCodetext):
            """!
            Initializes a new instance of the {@code MailmarkCodetext} class.
            :param mailmarkCodetext:
            """

            java_class_link = jpype.JClass(self.javaClassName)
            javaClass = None
            if mailmarkCodetext == None:
                  javaClass = java_class_link()
            else:
                  javaClass = java_class_link(mailmarkCodetext.getJavaClass())
            super().__init__(javaClass)

      def init(self):
            pass

      def getConstructedCodetext(self):
            """
            Construct codetext from Mailmark data.

            :return: Constructed codetext
            """
            return self.getJavaClass().getConstructedCodetext()

      def initFromString(self, constructedCodetext):
            """!
            Initializes Mailmark data from constructed codetext.
            :param constructedCodetext: Constructed codetext
            :return:
            """
            self.getJavaClass().initFromString(constructedCodetext)

      def getBarcodeType(self):
            """
            Gets barcode type.
            :return: Barcode type.
            """
            return self.getJavaClass().getBarcodeType()

class Mailmark2DCodetext(IComplexCodetext):

      javaClassName = "com.aspose.mw.barcode.complexbarcode.MwMailmark2DCodetext"

      @staticmethod
      def construct(javaClass):
            jsClass = Mailmark2DCodetext()
            jsClass.setJavaClass(javaClass)
            return jsClass

      def getUPUCountryID(self):
            """!
            Identifies the UPU Country ID.Max length: 4 characters.
            @return Country ID            
            """
            return self.getJavaClass().getUPUCountryID()

      def setUPUCountryID(self, value):
            """!
                Identifies the UPU Country ID.Max length: 4 characters.
                @param value Country ID
            """
            self.getJavaClass().setUPUCountryID(value)

      def getInformationTypeID(self):
            """!
            Identifies the Royal Mail Mailmark barcode payload for each product type.
            Valid Values:

            “0” - Domestic Sorted &amp; Unsorted
            “A” - Online Postage
            “B” - Franking
            “C” - Consolidation

            @return Information type ID
            """
            return self.getJavaClass().getInformationTypeID()

      def setInformationTypeID(self, value):
            """!
            Identifies the Royal Mail Mailmark barcode payload for each product type.
            Valid Values:

            “0” - Domestic Sorted &amp; Unsorted
            “A” - Online Postage
            “B” - Franking
            “C” - Consolidation

            @param value Information type ID
            """
            self.getJavaClass().setInformationTypeID(value)

      def getVersionID(self):
            """!
            Identifies the  barcode version as relevant to each Information Type ID.
            Valid Values:

            Currently “1”.
            “0” &amp; “2” to “9” and “A” to “Z” spare reserved for potential future use.

            @return Version ID
            """
            return self.getJavaClass().getVersionID()

      def setVersionID(self, value):
            """!
            Identifies the  barcode version as relevant to each Information Type ID.
            Valid Values:

            Currently “1”.
            “0” &amp; “2” to “9” and “A” to “Z” spare reserved for potential future use.

            @param value Version ID
            """
            self.getJavaClass().setVersionID(value)

      def getclass(self):
            """!
            Identifies the class of the item.

            Valid Values:
            “1” - 1C (Retail)
            “2” - 2C (Retail)
            “3” - Economy (Retail)
            “5” - Deffered (Retail)
            “8” - Premium (Network Access)
            “9” - Standard (Network Access)

            @return class of the item
            """
            return self.getJavaClass().getclass()

      def setclass(self, value):
            """!
            Identifies the class of the item.
            :param value: Valid Values:
            “1” - 1C (Retail)
            “2” - 2C (Retail)
            “3” - Economy (Retail)
            “5” - Deffered (Retail)
            “8” - Premium (Network Access)
            “9” - Standard (Network Access)
            :return: class of the item
            """
            self.getJavaClass().setclass(value)

      def getSupplyChainID(self):
            """!
            Identifies the unique group of customers involved in the mailing.
            Max value: 9999999.

            @return Supply chain ID
            """
            return self.getJavaClass().getSupplyChainID()

      def setSupplyChainID(self, value):
            """!
            Identifies the unique group of customers involved in the mailing.
            Max value: 9999999.
            :param value: Supply chain ID
            """
            self.getJavaClass().setSupplyChainID(value)

      def getItemID(self):
            """!
            Every Mailmark barcode is required to carry an ID
            Max value: 99999999.

            :return: item within the Supply Chain ID
            """
            return self.getJavaClass().getItemID()

      def setItemID(self, value):
            """!
            Identifies the unique item within the Supply Chain ID.
            Every Mailmark barcode is required to carry an ID
            Max value: 99999999.
            """
            self.getJavaClass().setItemID(value)

      def getDestinationPostCodeAndDPS(self):
            """!
            Contains the Postcode of the Delivery Address with DPS
                                                           * If inland the Postcode/DP contains the following number of characters.
            Area (1 or 2 characters) District(1 or 2 characters)
            Sector(1 character) Unit(2 characters) DPS (2 characters).
            The Postcode and DPS must comply with a valid PAF® format.

            @return the Postcode of the Delivery Address with DPS
            """
            return self.getJavaClass().getDestinationPostCodeAndDPS()

      def setDestinationPostCodeAndDPS(self, value):
           """!
           Contains the Postcode of the Delivery Address with DPS
           If inland the Postcode/DP contains the following number of characters.
           Area (1 or 2 characters) District(1 or 2 characters)
           Sector(1 character) Unit(2 characters) DPS (2 characters).
           The Postcode and DPS must comply with a valid PAF® format.
           :param value: the Postcode of the Delivery Address with DPS
           """
           self.getJavaClass().setDestinationPostCodeAndDPS(value)

      def getRTSFlag(self):
            """!
            Flag which indicates what level of Return to Sender service is being requested.
            @return RTS Flag
            """
            return self.getJavaClass().getRTSFlag()

      def setRTSFlag(self, value):
            """!
            Flag which indicates what level of Return to Sender service is being requested.
            :param value: RTS Flag
            """
            self.getJavaClass().setRTSFlag(value)

      def getReturnToSenderPostCode(self):
            """!
            Contains the Return to Sender Post Code but no DPS.
            The PC(without DPS) must comply with a PAF® format.
            :return: Return to Sender Post Code but no DPS
            """
            return self.getJavaClass().getReturnToSenderPostCode()

      def setReturnToSenderPostCode(self, value):
            """!
            Contains the Return to Sender Post Code but no DPS.
            The PC(without DPS) must comply with a PAF® format.
            :param value: Return to Sender Post Code but no DPS
            """
            self.getJavaClass().setReturnToSenderPostCode(value)

      def getCustomerContent(self):
            """!
             Optional space for use by customer.

             Max length by Type:
             Type 7: 6 characters
             Type 9: 45 characters
             Type 29: 25 characters

            :return: Customer content
            """
            return self.getJavaClass().getCustomerContent()

      def setCustomerContent(self, value):
            """!
            Optional space for use by customer.

            Max length by Type:
            Type 7: 6 characters
            Type 9: 45 characters
            Type 29: 25 characters

            @param value  Customer content
            """
            self.getJavaClass().setCustomerContent(value)

      def getCustomerContentEncodeMode(self):
            """!
            Encode mode of Datamatrix barcode.
            Default value: DataMatrixEncodeMode.C40.

            @return Encode mode of Datamatrix barcode.
            """
            return Generation.DataMatrixEncodeMode(self.getJavaClass().getCustomerContentEncodeMode())

      def setCustomerContentEncodeMode(self, value):
            """!
            Encode mode of Datamatrix barcode.
            Default value: DataMatrixEncodeMode.C40.
            :param value: Encode mode of Datamatrix barcode.
            """
            self.getJavaClass().setCustomerContentEncodeMode(value.value)

      def getDataMatrixType(self):
            """!
            2D Mailmark Type defines size of Data Matrix barcode.
            :return: Size of Data Matrix barcode
            """
            return Mailmark2DType(self.getJavaClass().getDataMatrixType())

      def setDataMatrixType(self, value):
            """!
            2D Mailmark Type defines size of Data Matrix barcode.
            :param value: Size of Data Matrix barcode
            """
            self.getJavaClass().setDataMatrixType(value.value)

      def __init__(self):
            """!
            Create default instance of Mailmark2DCodetext class.
            """
            javaMailmark2DCodetext = jpype.JClass(self.javaClassName)
            self.javaClass = javaMailmark2DCodetext()
            super().__init__(self.javaClass)
            self.init()

      def init(self):
            pass

      def getConstructedCodetext(self):
            """!
            Construct codetext from Mailmark data.
            :return: Constructed codetext
            """
            return self.getJavaClass().getConstructedCodetext()

      def initFromString(self, constructedCodetext):
            """!
            Initializes Mailmark data from constructed codetext.
            :param constructedCodetext: constructedCodetext Constructed codetext.
            """
            self.getJavaClass().initFromString(constructedCodetext)

      def getBarcodeType(self):
            """!
            Gets barcode type.
            :return: Barcode type.
            """
            return Generation.EncodeTypes.DATA_MATRIX

class Mailmark2DType(Enum):
      """!
      2D Mailmark Type defines size of Data Matrix barcode
      """

      AUTO = 0
      """!
      Auto determine
      """

      TYPE_7 = 1
      """!
      24 x 24 modules
      """

      TYPE_9 = 2
      """!
      32 x 32 modules
      """

      TYPE_29 = 3
      """!
      16 x 48 modules
      """