import boto3
from botocore.exceptions import ClientError
import os, platform

class SESSender:
    def __init__(self,sendto=None, fromaddr=None, message_txt=None, aws_region=None, fromname=None, msgsubject=None, message_html=None):
        # Initialize check variable for credentials
        self.aws_creds_present = False

        # Initialize check variable for argument validation
        self.required_args_present = False

        # set instance variables based on what was passed into __init__()
        self.sendto = sendto
        self.fromaddr = fromaddr
        self.message_txt = message_txt
        self.aws_region = aws_region
        self.fromname = fromname
        self.msgsubject = msgsubject
        self.message_html = message_html


    
    def ses_validate(self):
        # Returning False indicates an error. Returning True indicates everything was validated.

        # Only the arguments checked below are required.        
        if self.sendto == None:
            print("Error: Missing send to address in the SESSender class's __init__() method. This argument is required.")
            return False
        if self.fromaddr == None:
            print("Error: Missing fromaddr in the SESSender class's __init__() method. This argument is required.")
            return False
        
        if self.message_txt == None:
            print("Error: Missing message_txt in the SESSender class's __init__() method. This argument is required.")
            return False
        
        if self.aws_region == None:
            print("Error: aws_region is missing in the SESSender class's __init__() method. This argument is required.")
            return False
        
        # if we made it this far, all of our required arguments are present
        self.required_args_present = True

        # ---- AWS Credentials Validations ----        
        # Check for environment variables first
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            self.aws_creds_present = True
            return True
        
        # Since we don't have the environment variables we need present, we will need to use a credentials file
        # Start by determining the OS of the system running this application to determine the expected path to
        # the credentials file.                      
        # If the OS is not Linux or Windows, print error and stop routine. We are not supporting other operating systems
        if platform.system() != "Linux" and platform.system() != "Windows":
            print("\nError: We don't recognize your operating system. py-basic-ses supports Windows or Linux.\n")
            return False

        # determine the expected path to the credentials file based on the operating system
        if platform.system() == "Linux":
            # using expanduser() method to convert ~ into /home/<username>
            self.credpath = os.path.expanduser("~/.aws/credentials")
                    
        if platform.system() == "Windows":
            self.credpath = "C:\\Users\\" + os.getlogin() + "\\.aws\\credentials"

        # store some messages to use later
        cred_instructions_msg = ("\nIn order to authenticate with AWS SES, you have two options:\n"
                                "  1) Set environment variables of AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY with correct values\n"
                                "  2) Create a credentials file at " + self.credpath + " containing\n"
                                "       [default]\n"
                                "        aws_access_key_id = your-access-key-here\n"
                                "        aws_secret_access_key = your-secret-access-key-here\n")
                                

        cred_readme_msg = ("\nFor help setting up IAM users on AWS, retrieving credentials, and setting policies, "
                        "checkout the README for py-basic-ses at \nhttps://github.com/shinyshoes404/py-basic-ses\n")

        
        # does the path exist?
        if os.path.exists(self.credpath) == False:
            # if not, print a helpful error message, and bail out of this routine.
            print("\nError: There is a problem with your AWS credentials.")
            print(cred_instructions_msg)
            print(cred_readme_msg)
            return False
        else:
            # is credentials a file?
            if os.path.isfile(self.credpath) == False:
                # if not, print a helpful error message and bail out of this routine.
                print("\nError: There is a problem with your AWS credentials.")
                print(self.credpath + " is not a file.")
                print(cred_instructions_msg)
                print(cred_readme_msg)
                return False

            else:
                # do we have read access on the credentials file?
                if os.access(self.credpath, os.R_OK) == False:
                    # if not, print a helpful error message and bail out of this routine.
                    print("\nError: Your credentials file exists, and is in the right place, but you don't have access to read its contents. Please fix this permissions issue.")
                    print(cred_instructions_msg)
                    print(cred_readme_msg)
                    return False
                else:
                    # Read the contents of the file and look for aws_access_key_id and aws_secret_access_key
                    # Remove any spaces in our string variable to prep for the .find() method.
                    # In the credentials file, there can be as many spaces as you want between the key = value, but we need
                    # to make sure that the key and = are present. If they are not, then the boto3 library will throw an error
                    with open(self.credpath, "r") as cred_file:
                        cred_content = cred_file.read().replace(" ","")
                        
                    # look for aws_access_key_id= and aws_secret_access_key=
                    if cred_content.find("aws_access_key_id=") != -1 and cred_content.find("aws_secret_access_key=") != -1 and cred_content.find("[default]") != -1:
                        self.aws_creds_present = True
                        return True
                    else:
                        print("\nError: Your credentials file is missing something we need.")
                        print("Make sure your file contains all of the required items.")
                        print(cred_instructions_msg)
                        print(cred_readme_msg)
                        return False
        
        

    def send_email(self):

        # check for AWS cred flag
        if self.aws_creds_present == False and self.required_args_present == False:
            # if credentials have not ben validated, print error message and stop routine.
            print("Error: You did not instantiate the SESSender clsss correctly, and you need to fix your credentials before trying to send an email.\n")
            return False
        
        if self.aws_creds_present == False:
            print("Error: You need to fix your credentials before trying to send an email.\n")
            return False
        
        # check required arguments flag
        if self.required_args_present == False:
            print("Error: You are missing required arguments to instantiate the SESSender class.\n")
            return False

        # Replace sender@example.com with your "From" address.
        # This address must be verified with Amazon SES.
        # if a fromname was provided build out 'Sender Name <senderaddr@email.com>' format
        if self.fromname == None or self.fromname == "":
            self.SENDER = self.fromaddr
        else:
            self.SENDER = self.fromname + " <" + self.fromaddr + ">"        

        # Replace recipient@example.com with a "To" address. If your account 
        # is still in the sandbox, this address must be verified.
        self.RECIPIENT = self.sendto
        
        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        self.AWS_REGION = self.aws_region

        # The subject line for the email.
        if self.msgsubject == None:
            self.SUBJECT = ""
        else:
            self.SUBJECT = self.msgsubject

        # The email body for recipients with non-HTML email clients.
        self.BODY_TEXT = self.message_txt
                    
        # The HTML body of the email.
        if self.message_html == None:
            self.BODY_HTML = self.message_txt
        else:
            self.BODY_HTML = self.message_html                        

        # The character encoding for the email.
        self.CHARSET = "UTF-8"

        # Create a new SES resource and specify a region.
        self.client = boto3.client('ses',region_name=self.AWS_REGION)
        

        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        self.RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.CHARSET,
                            'Data': self.BODY_HTML,
                        },
                        'Text': {
                            'Charset': self.CHARSET,
                            'Data': self.BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': self.CHARSET,
                        'Data': self.SUBJECT,
                    },
                },
                Source=self.SENDER,
                
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            return True

    