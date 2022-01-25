from zohoSolCon import auth
import contacts
import contact_persons
import estimates


def test_contacts(token):
    # Contact creation
    data_object = {"contact_name": "Test Contact"}
    
    org_id="760546410"
    token, status, response = contacts.create_contact(token, org_id, data_object)
    print("Create Contact\n")
    print(response)
    contact_id = response['contact_id']
    token, page_context, records = contacts.get_contacts(token, org_id)
    print("Get Contacts\n")
    print(records)

    data_object = {'company_name': "Updated Company Name"}

    token, status, contact = contacts.update_contact(token, org_id, contact_id, data_object)
    print("Update Contact\n")
    print(contact)

    
    token, contact = contacts.get_contact(token, org_id, contact_id)
    print("Get Contact\n")
    print(contact)

    
    token, message = contacts.mark_status(token, org_id, contact_id, "inactive")

    print("Mark status\n")
    print(message)

    

def main():
    client_id = "1000.0VNUXZ0W47OW228LHBAJZ7RFLC6T1O"
    secret = "6920f0df429b5873910c4561dd9273b0344d1872cc"
    grant ="1000.1c95ac134c54c233dbdfff4c8dcbde90.da32af6be9a9b7e589e38458c5a0ce63"
    token = auth.Token(client_id, secret, grant_token=None, refresh_token='1000.7f41f25f0f8cc4c0086daed2f192ca48.d4381d05df5a5baf313447cdea55a3cb')
    print(token.refresh)
    test_contacts(token)



if __name__ == "__main__":
    main()

    
