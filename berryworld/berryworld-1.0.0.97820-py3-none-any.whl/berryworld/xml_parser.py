class XMLparser:
    """ Create an XML file according to a certain dictionary """

    def __init__(self, dict_df, main_cat="report", child="records"):
        """ This function takes a DataFrame an stores it as an xml
        :param dict_df: Dictionary of DataFrames as output from the ETL
        :return: None
        """
        self.main_cat = main_cat
        self.child = child
        aux_xml = '\n'.join(dict_df.apply(self.conv_xml, axis=1))
        xml = "\n" + "<%s>" % self.main_cat + "\n" + aux_xml + ("\n</%s>" % self.main_cat)
        self.xml = '<?xml version="1.0" encoding="UTF-8"?>' + xml

    def conv_xml(self, df):
        """ Convert each row to XML
        :param df: DataFrame row
        :return: Transformed row
        """
        xml = ["<%s>" % self.child]
        for field in df.index:
            xml.append('  <%s>%s</%s>' % (field, df[field], field))
        xml.append("</%s>" % self.child)
        return '\n'.join(xml)
